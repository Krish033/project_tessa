"use client";

import Navbar from "@/components/layouts/Navbar";
import React, { Suspense } from "react";
import { useParams } from "next/navigation";
import { useChat, useProject } from "@/lib/hooks";

function ChatIdNavbar() {
  const params = useParams();
  const chatId = (params?.chatId as string) || "";
  const { data: chat } = useChat(chatId);
  const projectId = chat?.project_id || "";
  const { data: project } = useProject(projectId);

  const breadcrumbs = [];
  if (project) {
    breadcrumbs.push({
      label: project.name,
      href: `/projects/${project.id}`,
    });
  }
  breadcrumbs.push({
    label: chat?.title || "Conversation",
    hasDropdown: true,
  });

  return <Navbar breadcrumbs={breadcrumbs} />;
}

export default function ChatIdLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="flex-1 flex flex-col min-h-0 h-full overflow-hidden">
      <Suspense fallback={<Navbar />}>
        <ChatIdNavbar />
      </Suspense>
      <div className="flex-1 flex flex-col min-h-0 overflow-hidden relative">
        {children}
      </div>
    </div>
  );
}
