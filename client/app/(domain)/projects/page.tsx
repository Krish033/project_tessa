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
import { useProjects, useCreateProject } from "@/lib/hooks";

export default function ProjectsPage() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const { data: projects = [], isLoading } = useProjects();
  const createProjectMutation = useCreateProject();

  const filteredProjects = projects.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
      {isLoading ? (
        <div className="text-[#888888] text-[14px]">Loading projects...</div>
      ) : filteredProjects.length === 0 ? (
        <div className="text-[#666666] text-[14px]">No projects yet. Click &quot;New project&quot; to create one.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredProjects.map((project) => (
            <Link
              key={project.id}
              href={`/projects/${project.id}`}
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
                    {project.updated_at
                      ? new Date(project.updated_at).toLocaleDateString()
                      : "Recently"}
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
      )}

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreate={async ({ name, description }) => {
          try {
            await createProjectMutation.mutateAsync({ name, description });
          } catch (err) {
            console.error("Failed to create project", err);
          }
        }}
      />
    </div>
  );
}
