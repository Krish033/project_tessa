"use client";

import React, { useEffect, useRef } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Settings02Icon,
  GlobalIcon,
  HelpCircleIcon,
  ArrowUp02Icon,
  InformationCircleIcon,
  Logout03Icon,
  ArrowRight01Icon,
} from "@hugeicons/core-free-icons";

interface ProfileDropdownProps {
  isOpen: boolean;
  onClose: () => void;
  email?: string;
  onOpenSettings?: () => void;
  onLogout?: () => void;
}

// Exact match SVG for monitor + phone device pair icon
function DevicePairIcon({ className = "text-[#cccccc]" }: { className?: string }) {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      {/* Monitor frame */}
      <path d="M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Z" />
      {/* Monitor base stand */}
      <path d="M8 20h8M12 16v4" />
      {/* Small phone overlay in foreground */}
      <rect x="15" y="11" width="6" height="9" rx="1.2" fill="#2b2b2b" />
      <rect x="15" y="11" width="6" height="9" rx="1.2" />
    </svg>
  );
}

export default function ProfileDropdown({
  isOpen,
  onClose,
  email = "srik51977@gmail.com",
  onOpenSettings,
  onLogout,
}: ProfileDropdownProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  // Close on outside click and Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
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
      className="absolute bottom-full left-1 mb-2.5 w-[285px] bg-[#272727] text-[#e6e6e6] rounded-2xl p-1.5 shadow-[0_16px_40px_rgba(0,0,0,0.7)] border border-[#373737] font-mono text-[13px] z-50 select-none animate-in fade-in zoom-in-95 duration-100"
    >
      {/* User Email Header */}
      <div className="px-3 pt-2.5 pb-2 text-[12px] text-[#8e8e8e] truncate font-normal">
        {email}
      </div>

      {/* Menu Group 1: Settings, Language, Get help */}
      <div className="space-y-0.5">
        <button
          type="button"
          onClick={() => {
            onOpenSettings?.();
            onClose();
          }}
          className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-[#383838] text-white transition-colors cursor-pointer group"
        >
          <div className="flex items-center gap-2.5">
            <HugeiconsIcon
              icon={Settings02Icon}
              size={17}
              strokeWidth={1.8}
              className="text-[#cccccc] group-hover:text-white"
            />
            <span className="font-normal text-[13.5px]">Settings</span>
          </div>
          <span className="text-[11px] text-[#858585] font-mono tracking-tighter">
            Ctrl+Shift+,
          </span>
        </button>

        <button
          type="button"
          className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl hover:bg-[#383838] text-white transition-colors cursor-pointer group"
        >
          <HugeiconsIcon
            icon={GlobalIcon}
            size={17}
            strokeWidth={1.8}
            className="text-[#cccccc] group-hover:text-white"
          />
          <span className="font-normal text-[13.5px]">Language</span>
        </button>

        <button
          type="button"
          className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl hover:bg-[#383838] text-white transition-colors cursor-pointer group"
        >
          <HugeiconsIcon
            icon={HelpCircleIcon}
            size={17}
            strokeWidth={1.8}
            className="text-[#cccccc] group-hover:text-white"
          />
          <span className="font-normal text-[13.5px]">Get help</span>
        </button>
      </div>

      {/* Subtle Divider */}
      <div className="h-[1px] bg-[#383838] my-1.5 mx-1" />

      {/* Menu Group 2: Upgrade plan, Get apps and extensions, Learn more */}
      <div className="space-y-0.5">
        <button
          type="button"
          className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl hover:bg-[#383838] text-white transition-colors cursor-pointer group"
        >
          <div className="w-[17px] h-[17px] rounded-full border border-[#cccccc] group-hover:border-white flex items-center justify-center">
            <HugeiconsIcon
              icon={ArrowUp02Icon}
              size={11}
              strokeWidth={2.4}
              className="text-[#cccccc] group-hover:text-white"
            />
          </div>
          <span className="font-normal text-[13.5px]">Upgrade plan</span>
        </button>

        <button
          type="button"
          className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl hover:bg-[#383838] text-white transition-colors cursor-pointer group"
        >
          <DevicePairIcon className="text-[#cccccc] group-hover:text-white" />
          <span className="font-normal text-[13.5px]">Get apps and extensions</span>
        </button>

        <button
          type="button"
          className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-xl hover:bg-[#383838] text-white transition-colors cursor-pointer group"
        >
          <div className="flex items-center gap-2.5">
            <HugeiconsIcon
              icon={InformationCircleIcon}
              size={17}
              strokeWidth={1.8}
              className="text-[#cccccc] group-hover:text-white"
            />
            <span className="font-normal text-[13.5px]">Learn more</span>
          </div>
          <HugeiconsIcon
            icon={ArrowRight01Icon}
            size={14}
            strokeWidth={2}
            className="text-[#7c7c7c] group-hover:text-white"
          />
        </button>
      </div>

      {/* Subtle Divider */}
      <div className="h-[1px] bg-[#383838] my-1.5 mx-1" />

      {/* Menu Group 3: Log out */}
      <div>
        <button
          type="button"
          onClick={() => {
            onLogout?.();
            onClose();
          }}
          className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl hover:bg-[#383838] text-white transition-colors cursor-pointer group"
        >
          <HugeiconsIcon
            icon={Logout03Icon}
            size={17}
            strokeWidth={1.8}
            className="text-[#cccccc] group-hover:text-white"
          />
          <span className="font-normal text-[13.5px]">Log out</span>
        </button>
      </div>
    </div>
  );
}
