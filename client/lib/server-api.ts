import { ProjectItem, ChatItem } from "./api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Fetch all projects on the server with Next.js fetch cache and ISR tags.
 */
export async function getCachedProjects(): Promise<ProjectItem[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/projects/`, {
      next: { revalidate: 30, tags: ["projects"] },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.projects || [];
  } catch {
    return [];
  }
}

/**
 * Fetch a single project by ID on the server with Next.js fetch cache.
 */
export async function getCachedProject(id: string): Promise<ProjectItem | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/projects/${id}`, {
      next: { revalidate: 30, tags: [`project-${id}`] },
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.project || null;
  } catch {
    return null;
  }
}

/**
 * Fetch chats on the server with Next.js fetch cache.
 */
export async function getCachedChats(projectId?: string): Promise<ChatItem[]> {
  try {
    const url = new URL(`${API_BASE}/api/v1/chats/`);
    if (projectId) url.searchParams.set("project_id", projectId);

    const res = await fetch(url.toString(), {
      next: { revalidate: 15, tags: ["chats"] },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.chats || [];
  } catch {
    return [];
  }
}

/**
 * Fetch a single chat by ID on the server with Next.js fetch cache.
 */
export async function getCachedChat(id: string): Promise<ChatItem | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/chats/${id}`, {
      next: { revalidate: 15, tags: [`chat-${id}`] },
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.chat || null;
  } catch {
    return null;
  }
}
