"use client";

import React, { useState } from "react";
import Link from "next/link";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Search01Icon,
  ArrowUpDownIcon,
  Folder01Icon,
} from "@hugeicons/core-free-icons";
import CreateProjectModal from "@/components/shared/CreateProjectModal";

interface ProjectItem {
  id: string;
  name: string;
  lastUpdated: string;
  href?: string;
}

export default function ProjectsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [projects, setProjects] = useState<ProjectItem[]>([
    {
      id: "mysteries",
      name: "Mysteries",
      lastUpdated: "2 hours ago",
      href: "/projects/mysteries",
    },
  ]);

  return (
    <div className="min-h-full flex-1 bg-[#141414] text-white font-mono select-none px-8 py-7 md:px-12 md:py-8">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between pb-7">
        <h1 className="text-[26px] md:text-[28px] font-semibold text-white tracking-tight">
          Projects
        </h1>

        <div className="flex items-center gap-4">
          {/* Search Icon Button */}
          <button
            type="button"
            className="p-1.5 text-[#999999] hover:text-white transition-colors"
            title="Search projects"
          >
            <HugeiconsIcon icon={Search01Icon} size={18} strokeWidth={2} />
          </button>

          {/* Sort Icon Button */}
          <button
            type="button"
            className="p-1.5 text-[#999999] hover:text-white transition-colors"
            title="Sort projects"
          >
            <HugeiconsIcon icon={ArrowUpDownIcon} size={18} strokeWidth={2} />
          </button>

          {/* New Project Button */}
          <button
            type="button"
            onClick={() => setIsCreateOpen(true)}
            className="px-3.5 py-1.5 rounded-full bg-white text-black hover:bg-[#eaeaea] font-medium text-[13px] tracking-tight transition-colors shadow-sm cursor-pointer"
          >
            New project
          </button>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {projects.map((project) => (
          <Link
            key={project.id}
            href={project.href || "#"}
            className="relative flex items-center justify-between p-3.5 rounded-2xl bg-[#1e1e1e] hover:bg-[#252525] border border-[#2b2b2b] hover:border-[#383838] transition-all group overflow-hidden"
          >
            {/* Left Project Icon + Info */}
            <div className="flex items-center gap-3 min-w-0 pr-8">
              {/* Folder Icon badge container */}
              <div className="w-10 h-10 rounded-xl bg-[#262626] border border-[#303030] flex items-center justify-center shrink-0 text-[#a0a0a0] group-hover:text-white transition-colors">
                <HugeiconsIcon icon={Folder01Icon} size={19} strokeWidth={2} />
              </div>

              <div className="flex flex-col min-w-0">
                <span className="text-[14px] font-semibold text-[#f0f0f0] group-hover:text-white truncate">
                  {project.name}
                </span>
                <span className="text-[12px] text-[#787878] group-hover:text-[#949494] transition-colors truncate">
                  {project.lastUpdated}
                </span>
              </div>
            </div>

            {/* Folded / Dog-ear Corner Accent (Top-Right) */}
            <div className="absolute top-0 right-0 w-6 h-6 overflow-hidden pointer-events-none">
              <div className="absolute -top-3 -right-3 w-6 h-6 bg-[#2a2a2a] group-hover:bg-[#343434] rotate-45 border-b border-l border-[#3a3a3a] transition-colors" />
            </div>
          </Link>
        ))}
      </div>

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreate={({ name, description }) => {
          setProjects((prev) => [
            {
              id: name.toLowerCase().replace(/\s+/g, "-"),
              name,
              lastUpdated: "Just now",
              href: `/projects/${name.toLowerCase().replace(/\s+/g, "-")}`,
            },
            ...prev,
          ]);
        }}
      />
    </div>
  );
}
