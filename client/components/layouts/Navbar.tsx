"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Share01Icon,
  ChevronDownIcon,
  PinIcon,
  PencilEdit02Icon,
  Folder01Icon,
  Delete02Icon,
  ChevronRightIcon,
} from "@hugeicons/core-free-icons";

interface NavbarProps {
  breadcrumbs?: Array<{ label: string; href?: string; hasDropdown?: boolean }>;
  showShare?: boolean;
}

export default function Navbar({
  breadcrumbs = [
    { label: "Broward Partnership for kids", href: "/projects" },
    { label: "Calendar and post issues", hasDropdown: true },
  ],
  showShare = true,
}: NavbarProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click or Escape
  useEffect(() => {
    if (!isDropdownOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isDropdownOpen]);

  return (
    <header className="h-[46px] w-full flex items-center justify-between px-5 bg-[#181818] border-b border-[#262626] select-none text-[13px] font-mono shrink-0 relative z-30">
      <nav aria-label="Breadcrumb" className="flex items-center gap-2">
        {breadcrumbs.map((crumb, idx) => {
          const isLast = idx === breadcrumbs.length - 1;

          return (
            <React.Fragment key={`${crumb.label}-${idx}`}>
              {idx > 0 && (
                <span className="text-[#555555] font-light select-none">/</span>
              )}
              {isLast ? (
                <div className="relative flex items-center" ref={dropdownRef}>
                  <button
                    type="button"
                    onClick={() => {
                      if (crumb.hasDropdown) {
                        setIsDropdownOpen(!isDropdownOpen);
                      }
                    }}
                    className={`flex items-center gap-1.5 px-1.5 py-1 rounded-lg text-[#ececec] font-medium tracking-wide transition-colors cursor-pointer ${
                      isDropdownOpen ? "bg-[#282828] text-white" : "hover:bg-[#222222]"
                    }`}
                  >
                    <span>{crumb.label}</span>
                    {crumb.hasDropdown && (
                      <HugeiconsIcon
                        icon={ChevronDownIcon}
                        size={13}
                        strokeWidth={2}
                        className={`text-[#888888] transition-transform duration-150 ${
                          isDropdownOpen ? "rotate-180" : ""
                        }`}
                      />
                    )}
                  </button>

                  {/* Dropdown Menu Popup */}
                  {isDropdownOpen && (
                    <div className="absolute top-full left-0 mt-2 w-[220px] bg-[#222222] text-[#e0e0e0] border border-[#333333] rounded-2xl p-1.5 shadow-[0_16px_40px_rgba(0,0,0,0.85)] z-50 font-mono text-[13px] select-none animate-in fade-in zoom-in-95 duration-100">
                      {/* Pin */}
                      <button
                        type="button"
                        onClick={() => setIsDropdownOpen(false)}
                        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
                      >
                        <div className="flex items-center gap-2.5">
                          <HugeiconsIcon
                            icon={PinIcon}
                            size={15}
                            strokeWidth={1.8}
                            className="text-[#a0a0a0] group-hover:text-white"
                          />
                          <span className="font-normal text-[13px]">Pin</span>
                        </div>
                        <span className="text-[11px] text-[#787878] font-mono">P</span>
                      </button>

                      {/* Rename */}
                      <button
                        type="button"
                        onClick={() => setIsDropdownOpen(false)}
                        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
                      >
                        <div className="flex items-center gap-2.5">
                          <HugeiconsIcon
                            icon={PencilEdit02Icon}
                            size={15}
                            strokeWidth={1.8}
                            className="text-[#a0a0a0] group-hover:text-white"
                          />
                          <span className="font-normal text-[13px]">Rename</span>
                        </div>
                        <span className="text-[11px] text-[#787878] font-mono">R</span>
                      </button>

                      {/* Change project */}
                      <button
                        type="button"
                        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
                      >
                        <div className="flex items-center gap-2.5">
                          <HugeiconsIcon
                            icon={Folder01Icon}
                            size={15}
                            strokeWidth={1.8}
                            className="text-[#a0a0a0] group-hover:text-white"
                          />
                          <span className="font-normal text-[13px]">Change project</span>
                        </div>
                        <HugeiconsIcon
                          icon={ChevronRightIcon}
                          size={14}
                          strokeWidth={2}
                          className="text-[#777777] group-hover:text-white"
                        />
                      </button>

                      {/* Remove from project */}
                      <button
                        type="button"
                        onClick={() => setIsDropdownOpen(false)}
                        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
                      >
                        {/* Folder with remove minus icon */}
                        <svg
                          width="15"
                          height="15"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="text-[#a0a0a0] group-hover:text-white"
                        >
                          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                          <line x1="9" y1="14" x2="15" y2="14" />
                        </svg>
                        <span className="font-normal text-[13px]">Remove from project</span>
                      </button>

                      {/* Share chat */}
                      <button
                        type="button"
                        onClick={() => setIsDropdownOpen(false)}
                        className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl hover:bg-[#2e2e2e] text-[#f0f0f0] transition-colors cursor-pointer group"
                      >
                        <HugeiconsIcon
                          icon={Share01Icon}
                          size={15}
                          strokeWidth={1.8}
                          className="text-[#a0a0a0] group-hover:text-white"
                        />
                        <span className="font-normal text-[13px]">Share chat</span>
                      </button>

                      {/* Delete */}
                      <button
                        type="button"
                        onClick={() => setIsDropdownOpen(false)}
                        className="w-full flex items-center justify-between px-3 py-2 rounded-xl hover:bg-[#341d1d] text-[#ef4444] hover:text-[#f87171] transition-colors cursor-pointer group"
                      >
                        <div className="flex items-center gap-2.5">
                          <HugeiconsIcon
                            icon={Delete02Icon}
                            size={15}
                            strokeWidth={1.8}
                            className="text-[#ef4444] group-hover:text-[#f87171]"
                          />
                          <span className="font-normal text-[13px]">Delete</span>
                        </div>
                        <span className="text-[11px] text-[#ef4444]/60 font-mono">D</span>
                      </button>
                    </div>
                  )}
                </div>
              ) : crumb.href ? (
                <Link
                  href={crumb.href}
                  className="text-[#999999] hover:text-[#e0e0e0] transition-colors"
                >
                  {crumb.label}
                </Link>
              ) : (
                <span className="text-[#999999]">{crumb.label}</span>
              )}
            </React.Fragment>
          );
        })}
      </nav>

      {showShare && (
        <button
          type="button"
          className="flex items-center gap-1.5 text-[12.5px] text-[#a0a0a0] hover:text-white transition-colors cursor-pointer"
        >
          <HugeiconsIcon icon={Share01Icon} size={14} strokeWidth={2} />
          <span>Share</span>
        </button>
      )}
    </header>
  );
}
