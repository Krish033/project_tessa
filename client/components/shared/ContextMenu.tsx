"use client";

import React, { useEffect, useRef } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Attachment01Icon,
  Github01Icon,
} from "@hugeicons/core-free-icons";

interface ContextMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload?: () => void;
  onAddText?: () => void;
}

export default function ContextMenu({
  isOpen,
  onClose,
  onUpload,
  onAddText,
}: ContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  // Close on outside click or Escape key
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
      className="absolute top-full right-0 mt-2 w-[190px] bg-[#222222] text-[#e0e0e0] border border-[#333333] rounded-2xl p-1.5 shadow-[0_16px_40px_rgba(0,0,0,0.85)] z-50 font-mono text-[13px] select-none animate-in fade-in zoom-in-95 duration-100"
    >
      {/* Upload from device */}
      <button
        type="button"
        onClick={() => {
          onUpload?.();
          onClose();
        }}
        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group text-left"
      >
        <HugeiconsIcon
          icon={Attachment01Icon}
          size={16}
          strokeWidth={1.8}
          className="text-[#a0a0a0] group-hover:text-white shrink-0"
        />
        <span className="font-normal text-[13px]">Upload from device</span>
      </button>

      {/* Add text content */}
      <button
        type="button"
        onClick={() => {
          onAddText?.();
          onClose();
        }}
        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group text-left"
      >
        {/* Document text icon with lines */}
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-[#a0a0a0] group-hover:text-white shrink-0"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <line x1="10" y1="9" x2="8" y2="9" />
        </svg>
        <span className="font-normal text-[13px]">Add text content</span>
      </button>

      {/* GitHub */}
      <button
        type="button"
        onClick={onClose}
        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group text-left"
      >
        <HugeiconsIcon
          icon={Github01Icon}
          size={16}
          strokeWidth={1.8}
          className="text-[#a0a0a0] group-hover:text-white shrink-0"
        />
        <span className="font-normal text-[13px]">GitHub</span>
      </button>
    </div>
  );
}
