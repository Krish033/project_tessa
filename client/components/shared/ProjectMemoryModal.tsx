"use client";

import React, { useState, useEffect } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import { Cancel01Icon } from "@hugeicons/core-free-icons";

interface MemoryItem {
  id: string;
  title: string;
  snippet: string;
  updatedAt: string;
}

interface ProjectMemoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ProjectMemoryModal({
  isOpen,
  onClose,
}: ProjectMemoryModalProps) {
  const [useAccountMemory, setUseAccountMemory] = useState(true);

  const memories: MemoryItem[] = [
    {
      id: "mem-1",
      title: "Calendar Invites",
      snippet: "Krishna testing his app's...",
      updatedAt: "Updated 5 hours ago",
    },
    {
      id: "mem-2",
      title: "Broward Partnership fo...",
      snippet: "Broward Partnership for k...",
      updatedAt: "Updated 5 hours ago",
    },
  ];

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Memory"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/65 backdrop-blur-[2px] animate-in fade-in duration-150 select-none font-mono"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-[560px] bg-[#272727] text-[#ebebeb] rounded-2xl p-6 shadow-[0_24px_60px_rgba(0,0,0,0.85)] border border-[#383838] animate-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between pb-4">
          <h2 className="text-[15px] font-semibold text-[#f2f2f2] tracking-tight">
            Memory
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-[#8c8c8c] hover:text-white rounded-lg hover:bg-[#343434] transition-colors cursor-pointer"
            aria-label="Close"
          >
            <HugeiconsIcon icon={Cancel01Icon} size={16} strokeWidth={2} />
          </button>
        </div>

        {/* Memory Items List */}
        <div className="divide-y divide-[#333333] border-b border-[#333333]">
          {memories.map((mem) => (
            <div
              key={mem.id}
              className="py-3 px-1 flex items-center justify-between text-[13px] hover:bg-[#2e2e2e] rounded-xl transition-colors"
            >
              <div className="font-medium text-[#f0f0f0] truncate w-[160px]">
                {mem.title}
              </div>
              <div className="text-[#999999] truncate flex-1 px-3 text-[12.5px]">
                {mem.snippet}
              </div>
              <div className="text-[11.5px] text-[#777777] shrink-0">
                {mem.updatedAt}
              </div>
            </div>
          ))}
        </div>

        {/* Use Account Memory Toggle Section */}
        <div className="pt-4 flex items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="text-[13px] font-medium text-[#f0f0f0]">
              Use account memory
            </div>
            <p className="text-[12px] text-[#8e8e8e] leading-relaxed">
              Allow Claude to share memory between this project and your chats outside of projects.{" "}
              <button
                type="button"
                className="text-[#3b82f6] hover:underline cursor-pointer"
              >
                View account memory
              </button>
            </p>
          </div>

          {/* Toggle Switch */}
          <button
            type="button"
            role="switch"
            aria-checked={useAccountMemory}
            onClick={() => setUseAccountMemory(!useAccountMemory)}
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
              useAccountMemory ? "bg-[#2563eb]" : "bg-[#444444]"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                useAccountMemory ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
        </div>
      </div>
    </div>
  );
}
