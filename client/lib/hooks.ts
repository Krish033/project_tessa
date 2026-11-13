import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { projectsApi, chatsApi, settingsApi, ProjectItem, ChatItem, LLMItem } from "./api";

// ── Query Keys ────────────────────────────────────────────────

export const queryKeys = {
  projects: ["projects"] as const,
  project: (id: string) => ["projects", id] as const,
  chats: (projectId?: string) => ["chats", { projectId }] as const,
  chat: (id: string) => ["chats", id] as const,
  llms: ["settings", "llms"] as const,
};

// ── Projects Hooks ────────────────────────────────────────────

export function useProjects(initialData?: ProjectItem[]) {
  return useQuery({
    queryKey: queryKeys.projects,
    queryFn: projectsApi.getAll,
    initialData,
  });
}

export function useProject(id: string, initialData?: ProjectItem) {
  return useQuery({
    queryKey: queryKeys.project(id),
    queryFn: () => projectsApi.getById(id),
    enabled: !!id,
    initialData,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { name?: string; description?: string; instructions?: string } }) =>
      projectsApi.update(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
      queryClient.invalidateQueries({ queryKey: queryKeys.project(variables.id) });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
}

// ── Chats Hooks ───────────────────────────────────────────────

export function useChats(projectId?: string, initialData?: ChatItem[]) {
  return useQuery({
    queryKey: queryKeys.chats(projectId),
    queryFn: () => chatsApi.getAll(projectId),
    initialData,
  });
}

export function useChat(id: string, initialData?: ChatItem) {
  return useQuery({
    queryKey: queryKeys.chat(id),
    queryFn: () => chatsApi.getById(id),
    enabled: !!id,
    initialData,
  });
}

export function useCreateChat() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: chatsApi.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chats() });
      if (data.project_id) {
        queryClient.invalidateQueries({ queryKey: queryKeys.chats(data.project_id) });
        queryClient.invalidateQueries({ queryKey: queryKeys.project(data.project_id) });
        queryClient.invalidateQueries({ queryKey: queryKeys.projects });
      }
    },
  });
}

export function useUpdateChat() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { title?: string; project_id?: string | null } }) =>
      chatsApi.update(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chats() });
      queryClient.invalidateQueries({ queryKey: queryKeys.chat(variables.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
}

export function useDeleteChat() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: chatsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chats() });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
  });
}

export function useAddMessage(chatId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { role: string; content: string }) =>
      chatsApi.addMessage(chatId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.chat(chatId) });
    },
  });
}

// ── LLM Settings Hooks ────────────────────────────────────────

export function useLLMs() {
  return useQuery({
    queryKey: queryKeys.llms,
    queryFn: settingsApi.getLLMs,
  });
}

export function useCreateLLM() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.createLLM,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.llms });
    },
  });
}

export function useUpdateLLM() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<Omit<LLMItem, "id" | "created_at" | "updated_at">>;
    }) => settingsApi.updateLLM(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.llms });
    },
  });
}

export function useDeleteLLM() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.deleteLLM,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.llms });
    },
  });
}
