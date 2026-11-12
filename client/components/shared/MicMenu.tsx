"use client";

import React, { useEffect, useRef } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  MicOff01Icon,
  ChevronRightIcon,
} from "@hugeicons/core-free-icons";

interface MicMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function MicMenu({ isOpen, onClose }: MicMenuProps) {
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
      className="absolute bottom-full right-0 mb-3 w-[205px] bg-[#222222] text-[#e0e0e0] border border-[#333333] rounded-2xl p-2.5 shadow-[0_16px_40px_rgba(0,0,0,0.85)] z-50 font-mono select-none animate-in fade-in zoom-in-95 duration-100"
    >
      {/* Device Status: No devices found */}
      <div className="flex items-center gap-2.5 px-2 py-1 text-[#787878] text-[12.5px]">
        <HugeiconsIcon
          icon={MicOff01Icon}
          size={16}
          strokeWidth={1.8}
          className="text-[#666666] shrink-0"
        />
        <span className="font-normal text-[#888888]">No devices found</span>
      </div>

      {/* Dictation Settings Heading */}
      <div className="px-2 pt-3 pb-1 text-[11px] text-[#6e6e6e] uppercase tracking-wider font-medium">
        Dictation settings
      </div>

      {/* Language Auto */}
      <button
        type="button"
        className="w-full flex items-center justify-between px-2 py-1.5 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group text-[12.5px]"
      >
        <span className="font-normal text-[#d6d6d6]">Language</span>
        <div className="flex items-center gap-1 text-[#888888] group-hover:text-white">
          <span className="text-[12px] text-[#999999]">Auto</span>
          <HugeiconsIcon
            icon={ChevronRightIcon}
            size={13}
            strokeWidth={2}
            className="text-[#777777] group-hover:text-white"
          />
        </div>
      </button>
    </div>
  );
}
