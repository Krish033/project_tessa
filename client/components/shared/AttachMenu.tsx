"use client";

import React, { useEffect, useRef, useState } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Attachment01Icon,
  Camera01Icon,
  Folder01Icon,
  FileCodeIcon,
  Grid2X2Icon,
  GlobalIcon,
  ChevronRightIcon,
  Tick01Icon,
} from "@hugeicons/core-free-icons";

interface AttachMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadFiles?: () => void;
}

export default function AttachMenu({ isOpen, onClose, onUploadFiles }: AttachMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);
  const [webSearchEnabled, setWebSearchEnabled] = useState(true);

  // Close on outside click or Escape
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={menuRef}
      className="absolute bottom-full left-0 mb-3 w-[260px] bg-[#222222] text-[#e0e0e0] border border-[#333333] rounded-2xl p-1.5 shadow-[0_16px_40px_rgba(0,0,0,0.8)] z-50 font-mono text-[13px] select-none animate-in fade-in zoom-in-95 duration-100"
    >
      {/* Upload or add files */}
      <button
        type="button"
        onClick={() => {
          onUploadFiles?.();
          onClose();
        }}
        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
      >
        <div className="flex items-center gap-2.5">
          <HugeiconsIcon
            icon={Attachment01Icon}
            size={16}
            strokeWidth={1.8}
            className="text-[#a0a0a0] group-hover:text-white"
          />
          <span className="font-normal text-[13px]">Upload or add files</span>
        </div>
        <span className="text-[11px] text-[#787878] font-mono">Ctrl+U</span>
      </button>

      {/* Take a screenshot */}
      <button
        type="button"
        onClick={onClose}
        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
      >
        <HugeiconsIcon
          icon={Camera01Icon}
          size={16}
          strokeWidth={1.8}
          className="text-[#a0a0a0] group-hover:text-white"
        />
        <span className="font-normal text-[13px]">Take a screenshot</span>
      </button>

      {/* Add to project */}
      <button
        type="button"
        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
      >
        <div className="flex items-center gap-2.5">
          <HugeiconsIcon
            icon={Folder01Icon}
            size={16}
            strokeWidth={1.8}
            className="text-[#a0a0a0] group-hover:text-white"
          />
          <span className="font-normal text-[13px]">Add to project</span>
        </div>
        <HugeiconsIcon
          icon={ChevronRightIcon}
          size={14}
          strokeWidth={2}
          className="text-[#777777] group-hover:text-white"
        />
      </button>

      {/* Subtle Divider */}
      <div className="h-[1px] bg-[#2d2d2d] my-1 mx-1" />

      {/* Skills */}
      <button
        type="button"
        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
      >
        <div className="flex items-center gap-2.5">
          <HugeiconsIcon
            icon={FileCodeIcon}
            size={16}
            strokeWidth={1.8}
            className="text-[#a0a0a0] group-hover:text-white"
          />
          <span className="font-normal text-[13px]">Skills</span>
        </div>
        <HugeiconsIcon
          icon={ChevronRightIcon}
          size={14}
          strokeWidth={2}
          className="text-[#777777] group-hover:text-white"
        />
      </button>

      {/* Add connector */}
      <button
        type="button"
        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
      >
        <div className="flex items-center gap-2.5">
          <HugeiconsIcon
            icon={Grid2X2Icon}
            size={16}
            strokeWidth={1.8}
            className="text-[#a0a0a0] group-hover:text-white"
          />
          <span className="font-normal text-[13px]">Add connector</span>
        </div>
        <HugeiconsIcon
          icon={ChevronRightIcon}
          size={14}
          strokeWidth={2}
          className="text-[#777777] group-hover:text-white"
        />
      </button>

      {/* Design system */}
      <button
        type="button"
        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
      >
        <div className="flex items-center gap-2.5">
          {/* Half circle / design icon */}
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="text-[#a0a0a0] group-hover:text-white"
          >
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18V4c4.41 0 8 3.59 8 8s-3.59 8-8 8z" />
          </svg>
          <span className="font-normal text-[13px]">Design system</span>
        </div>
        <HugeiconsIcon
          icon={ChevronRightIcon}
          size={14}
          strokeWidth={2}
          className="text-[#777777] group-hover:text-white"
        />
      </button>

      {/* Add plugins */}
      <button
        type="button"
        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
      >
        {/* Plug icon */}
        <svg
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          className="text-[#a0a0a0] group-hover:text-white"
        >
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4" />
        </svg>
        <span className="font-normal text-[13px]">Add plugins</span>
      </button>

      {/* Subtle Divider */}
      <div className="h-[1px] bg-[#2d2d2d] my-1 mx-1" />

      {/* Web search toggle */}
      <button
        type="button"
        onClick={() => setWebSearchEnabled(!webSearchEnabled)}
        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
      >
        <div className="flex items-center gap-2.5">
          <HugeiconsIcon
            icon={GlobalIcon}
            size={16}
            strokeWidth={1.8}
            className="text-[#a0a0a0] group-hover:text-white"
          />
          <span className="font-normal text-[13px]">Web search</span>
        </div>
        {webSearchEnabled && (
          <HugeiconsIcon
            icon={Tick01Icon}
            size={15}
            strokeWidth={2.4}
            className="text-[#3b82f6]"
          />
        )}
      </button>
    </div>
  );
}
