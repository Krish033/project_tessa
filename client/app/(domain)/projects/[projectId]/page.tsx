"use client";

import React, { useState, Suspense, useRef } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { HugeiconsIcon } from "@hugeicons/react";
import SetProjectInstructionsModal from "@/components/shared/SetProjectInstructionsModal";
import ContextMenu from "@/components/shared/ContextMenu";
import AddTextContentModal from "@/components/shared/AddTextContentModal";
import ProjectMemoryModal from "@/components/shared/ProjectMemoryModal";
import {
  Add01Icon,
  Mic01Icon,
  ArrowDown01Icon,
  AudioWaveformIcon,
  MoreHorizontalIcon,
  User02Icon,
} from "@hugeicons/core-free-icons";

function ProjectDetailContent() {
  const params = useParams();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [prompt, setPrompt] = useState("");
  const [activeMode, setActiveMode] = useState<"Chat" | "Cowork">("Chat");
  const [isInstructionsOpen, setIsInstructionsOpen] = useState(false);
  const [isContextOpen, setIsContextOpen] = useState(false);
  const [isAddTextOpen, setIsAddTextOpen] = useState(false);
  const [isMemoryOpen, setIsMemoryOpen] = useState(false);
  const [instructionsText, setInstructionsText] = useState("");

  const recentChats = [
    {
      id: "black-dahlia",
      title: "The Black Dahlia murder case",
      timestamp: "2 hours ago",
      href: "/chats/black-dahlia",
    },
  ];

  return (
    <div className="min-h-full flex-1 bg-[#141414] text-white font-mono select-none px-6 py-6 md:px-12 md:py-8 overflow-y-auto">
      {/* Top Header / Project Title Bar */}
      <div className="flex items-start justify-between pb-3">
        <div>
          <h1 className="text-[28px] md:text-[32px] font-semibold text-white tracking-tight">
            Mysteries
          </h1>
          <p className="mt-2 text-[#cccccc] text-[13.5px] leading-relaxed max-w-3xl">
            This is a folder where i store my case reports on mysteries and crime detections
          </p>
          <p className="mt-2 text-[#999999] text-[13px] leading-relaxed max-w-3xl">
            i used to play the detective game when i am bored, like detect the previously solved cases, murders or crimes by my own, might ask clues_
          </p>
        </div>

        {/* Right Corner Fold Icon & More Actions */}
        <div className="flex items-center gap-3 shrink-0 pt-1">
          {/* Folded paper corner icon */}
          <div className="w-5 h-5 flex items-center justify-center">
            <svg
              className="w-5 h-5 text-white fill-white"
              viewBox="0 0 24 24"
            >
              <path d="M4 4h10l6 6v10H4V4z" />
            </svg>
          </div>

          <button
            type="button"
            className="p-1 text-[#888888] hover:text-white transition-colors"
            title="Project options"
          >
            <HugeiconsIcon icon={MoreHorizontalIcon} size={20} strokeWidth={2} />
          </button>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-6">
        {/* Left Column: Input Box & Recent Chats (span 8) */}
        <div className="lg:col-span-8 flex flex-col space-y-6">
          {/* Main Input Box Card */}
          <div className="w-full bg-[#1e1e1e] border border-[#2d2d2d] hover:border-[#383838] focus-within:border-[#444444] rounded-2xl p-3.5 transition-all shadow-xl">
            {/* Text area */}
            <div className="min-h-[58px] px-1 pt-0.5">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="How can I help you today?"
                rows={2}
                className="w-full bg-transparent resize-none border-none outline-none text-[#ececec] placeholder-[#666666] text-[14px] leading-relaxed font-mono"
              />
            </div>

            {/* Bottom Input Controls */}
            <div className="flex items-center justify-between pt-2 mt-1">
              {/* Left Controls: Add button + Mode Switcher */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  className="w-7 h-7 rounded-lg bg-transparent hover:bg-[#282828] text-[#8e8e8e] hover:text-white flex items-center justify-center transition-colors"
                  title="Add attachment"
                >
                  <HugeiconsIcon icon={Add01Icon} size={17} strokeWidth={2.2} />
                </button>

                {/* Chat / Cowork pill toggle */}
                <div className="flex items-center bg-[#151515] p-0.5 rounded-lg border border-[#2b2b2b] text-[12px]">
                  <button
                    type="button"
                    onClick={() => setActiveMode("Chat")}
                    className={`px-2.5 py-0.5 rounded-md transition-colors ${
                      activeMode === "Chat"
                        ? "bg-[#2c2c2c] text-white font-medium shadow-sm"
                        : "text-[#7f7f7f] hover:text-white"
                    }`}
                  >
                    Chat
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveMode("Cowork")}
                    className={`px-2.5 py-0.5 rounded-md transition-colors ${
                      activeMode === "Cowork"
                        ? "bg-[#2c2c2c] text-white font-medium shadow-sm"
                        : "text-[#7f7f7f] hover:text-white"
                    }`}
                  >
                    Cowork
                  </button>
                </div>
              </div>

              {/* Right Controls: Model picker + Voice buttons */}
              <div className="flex items-center gap-2.5 text-[#888888]">
                <button
                  type="button"
                  className="flex items-center gap-1.5 px-2 py-1 rounded-lg hover:bg-[#282828] hover:text-white transition-colors text-[12px]"
                >
                  <span className="font-medium text-[#cccccc]">Sonnet 3.5</span>
                  <span className="text-[#777777] text-[11px]">Medium</span>
                </button>

                <button
                  type="button"
                  className="flex items-center gap-0.5 p-1 rounded-lg hover:bg-[#282828] text-[#8e8e8e] hover:text-white transition-colors"
                  title="Voice input"
                >
                  <HugeiconsIcon icon={Mic01Icon} size={15} strokeWidth={2} />
                  <HugeiconsIcon icon={ArrowDown01Icon} size={11} strokeWidth={2.5} className="text-[#666666]" />
                </button>

                <button
                  type="button"
                  className="p-1 rounded-lg hover:bg-[#282828] text-[#8e8e8e] hover:text-white transition-colors"
                  title="Start live voice"
                >
                  <HugeiconsIcon icon={AudioWaveformIcon} size={16} strokeWidth={2} />
                </button>
              </div>
            </div>
          </div>

          {/* Recents Section */}
          <div className="pt-2">
            <h2 className="text-[12.5px] font-semibold text-[#888888] mb-3">
              Recents
            </h2>

            <div className="space-y-1">
              {recentChats.map((chat) => (
                <Link
                  key={chat.id}
                  href={chat.href}
                  className="flex items-center justify-between py-2.5 px-2 rounded-xl hover:bg-[#1a1a1a] transition-colors group"
                >
                  <span className="text-[13.5px] text-[#e0e0e0] group-hover:text-white font-medium">
                    {chat.title}
                  </span>
                  <span className="text-[12px] text-[#707070] group-hover:text-[#909090] transition-colors">
                    {chat.timestamp}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Instructions, Memory & Context Cards (span 4) */}
        <div className="lg:col-span-4 bg-[#1a1a1a] border border-[#262626] rounded-2xl p-4 flex flex-col space-y-6">
          {/* Instructions Box */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[13.5px] font-semibold text-white">Instructions</span>
              <button
                type="button"
                onClick={() => setIsInstructionsOpen(true)}
                className="p-1 rounded hover:bg-[#252525] text-[#888888] hover:text-white transition-colors cursor-pointer"
                title="Add instructions"
              >
                <HugeiconsIcon icon={Add01Icon} size={16} strokeWidth={2.2} />
              </button>
            </div>
            <p className="text-[12px] text-[#777777] leading-relaxed">
              {instructionsText || "Add instructions to tailor Claude's responses"}
            </p>
          </div>

          {/* Memory Section */}
          <div className="space-y-1.5 pt-1 border-t border-[#232323]">
            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-2">
                <span className="text-[13.5px] font-semibold text-white">Memory</span>
                <span className="inline-flex items-center gap-1.5 text-[11px] px-2 py-0.5 rounded-md bg-[#242424] text-[#8e8e8e] border border-[#303030]">
                  <HugeiconsIcon icon={User02Icon} size={11} strokeWidth={2} />
                  <span>Only you</span>
                </span>
              </div>
              <button
                type="button"
                onClick={() => setIsMemoryOpen(true)}
                className="text-[12.5px] font-semibold text-white hover:text-[#cccccc] transition-colors cursor-pointer"
              >
                View memory
              </button>
            </div>
            <p className="text-[12px] text-[#777777] leading-relaxed">
              Project memory will show here after a few chats.
            </p>
          </div>

          {/* Context Section */}
          <div className="space-y-2.5 pt-1 border-t border-[#232323]">
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
            />

            <div className="flex items-center justify-between pt-2 relative">
              <span className="text-[13.5px] font-semibold text-white">Context</span>
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setIsContextOpen(!isContextOpen)}
                  className={`p-1 rounded text-[#888888] hover:text-white transition-colors cursor-pointer ${
                    isContextOpen ? "text-white bg-[#252525]" : "hover:bg-[#252525]"
                  }`}
                  title="Add context"
                >
                  <HugeiconsIcon icon={Add01Icon} size={16} strokeWidth={2.2} />
                </button>

                {/* Context Menu Popup */}
                <ContextMenu
                  isOpen={isContextOpen}
                  onClose={() => setIsContextOpen(false)}
                  onUpload={() => fileInputRef.current?.click()}
                  onAddText={() => setIsAddTextOpen(true)}
                />
              </div>
            </div>

            {/* Context Dropzone / Placeholder Box */}
            <div className="w-full bg-[#141414] border border-[#2b2b2b] rounded-xl p-6 flex flex-col items-center justify-center text-center">
              {/* Stacked Documents Graphic */}
              <div className="relative w-16 h-12 mb-3">
                <div className="absolute left-1 top-2 w-8 h-9 rounded bg-[#252525] border border-[#353535] flex items-center justify-center">
                  <div className="w-4 space-y-1">
                    <div className="h-0.5 bg-[#4a4a4a] rounded" />
                    <div className="h-0.5 bg-[#4a4a4a] rounded" />
                    <div className="h-0.5 bg-[#4a4a4a] rounded" />
                  </div>
                </div>
                <div className="absolute left-4 top-1 w-8 h-9 rounded bg-[#2e2e2e] border border-[#404040] flex items-center justify-center shadow-md">
                  <div className="w-4 space-y-1">
                    <div className="h-0.5 bg-[#606060] rounded" />
                    <div className="h-0.5 bg-[#606060] rounded" />
                    <div className="h-0.5 bg-[#606060] rounded" />
                  </div>
                </div>
                <div className="absolute left-7 top-0 w-8 h-9 rounded bg-[#383838] border border-[#4a4a4a] flex items-center justify-center shadow-lg">
                  <span className="text-[9px] text-[#888888]">+</span>
                </div>
              </div>

              <p className="text-[12px] text-[#808080] leading-relaxed max-w-[200px]">
                Add PDFs, documents, or other text to reference in this project.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Set Project Instructions Modal */}
      <SetProjectInstructionsModal
        isOpen={isInstructionsOpen}
        onClose={() => setIsInstructionsOpen(false)}
        projectName="Broward Partnership for kids"
        initialInstructions={instructionsText}
        onSave={(saved) => setInstructionsText(saved)}
      />

      {/* Add Text Content Modal */}
      <AddTextContentModal
        isOpen={isAddTextOpen}
        onClose={() => setIsAddTextOpen(false)}
        onAdd={({ title, content }) => {
          console.log("Added text content:", title, content);
        }}
      />

      {/* Project Memory Modal */}
      <ProjectMemoryModal
        isOpen={isMemoryOpen}
        onClose={() => setIsMemoryOpen(false)}
      />
    </div>
  );
}

export default function ProjectDetailPage() {
  return (
    <Suspense fallback={<div className="h-full bg-[#141414]" />}>
      <ProjectDetailContent />
    </Suspense>
  );
}
