import client from "./axios";

export interface ChatItem {
  id: string;
  title: string;
  project_id?: string | null;
  user_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  messages?: Array<{
    id: string;
    role: string;
    content: string;
    created_at?: string | null;
  }>;
}

export interface LLMItem {
  id: string;
  name: string;
  provider: string; // "ollama" | "openai" | "anthropic" | "custom"
  model_name: string;
  url: string;
  port?: number | null;
  auth_key?: string | null;
  temperature?: number;
  max_tokens?: number;
  is_default?: boolean;
  extra_headers?: Record<string, string>;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface ProjectItem {
  id: string;
  name: string;
  description?: string | null;
  instructions?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  chats?: Array<{
    id: string;
    title: string;
    created_at?: string | null;
    updated_at?: string | null;
  }>;
}

// ── Projects API ──────────────────────────────────────────────

export const projectsApi = {
  getAll: async (): Promise<ProjectItem[]> => {
    const res = await client.get<{ projects: ProjectItem[] }>("/api/v1/projects/");
    return res.data.projects || [];
  },

  getById: async (projectId: string): Promise<ProjectItem> => {
    const res = await client.get<{ project: ProjectItem }>(`/api/v1/projects/${projectId}`);
    return res.data.project;
  },

  create: async (data: { name: string; description?: string; instructions?: string }): Promise<ProjectItem> => {
    const res = await client.post<{ project: ProjectItem }>("/api/v1/projects/", data);
    return res.data.project;
  },

  update: async (projectId: string, data: { name?: string; description?: string; instructions?: string }): Promise<ProjectItem> => {
    const res = await client.patch<{ project: ProjectItem }>(`/api/v1/projects/${projectId}`, data);
    return res.data.project;
  },

  delete: async (projectId: string): Promise<void> => {
    await client.delete(`/api/v1/projects/${projectId}`);
  },
};

// ── Chats API ─────────────────────────────────────────────────

export const chatsApi = {
  getAll: async (projectId?: string): Promise<ChatItem[]> => {
    const res = await client.get<{ chats: ChatItem[] }>("/api/v1/chats/", {
      params: projectId ? { project_id: projectId } : undefined,
    });
    return res.data.chats || [];
  },

  getById: async (chatId: string): Promise<ChatItem> => {
    const res = await client.get<{ chat: ChatItem }>(`/api/v1/chats/${chatId}`);
    return res.data.chat;
  },

  create: async (data?: { title?: string; project_id?: string; initial_message?: string }): Promise<ChatItem> => {
    const res = await client.post<{ chat: ChatItem }>("/api/v1/chats/", data || {});
    return res.data.chat;
  },

  update: async (chatId: string, data: { title?: string; project_id?: string | null }): Promise<ChatItem> => {
    const res = await client.patch<{ chat: ChatItem }>(`/api/v1/chats/${chatId}`, data);
    return res.data.chat;
  },

  delete: async (chatId: string): Promise<void> => {
    await client.delete(`/api/v1/chats/${chatId}`);
  },

  addMessage: async (chatId: string, data: { role: string; content: string }) => {
    const res = await client.post<{ message: any }>(`/api/v1/chats/${chatId}/messages`, data);
    return res.data.message;
  },
};

// ── Settings API (LLMs, etc.) ──────────────────────────────────

export const settingsApi = {
  getLLMs: async (): Promise<LLMItem[]> => {
    const res = await client.get<{ llms: LLMItem[] }>("/api/v1/settings/llms");
    return res.data.llms || [];
  },

  createLLM: async (data: Omit<LLMItem, "id" | "created_at" | "updated_at">): Promise<LLMItem> => {
    const res = await client.post<{ llm: LLMItem }>("/api/v1/settings/llms", data);
    return res.data.llm;
  },

  updateLLM: async (
    id: string,
    data: Partial<Omit<LLMItem, "id" | "created_at" | "updated_at">>
  ): Promise<LLMItem> => {
    const res = await client.patch<{ llm: LLMItem }>(`/api/v1/settings/llms/${id}`, data);
    return res.data.llm;
  },

  deleteLLM: async (id: string): Promise<void> => {
    await client.delete(`/api/v1/settings/llms/${id}`);
  },
};

