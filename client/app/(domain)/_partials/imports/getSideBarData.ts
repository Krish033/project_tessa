import { getCachedProjects, getCachedChats } from "@/lib/server-api";

export default async function getSideBarData() {
  const [projects, chats] = await Promise.all([
    getCachedProjects(),
    getCachedChats(),
  ]);

  return {
    projects,
    chats,
  };
}
