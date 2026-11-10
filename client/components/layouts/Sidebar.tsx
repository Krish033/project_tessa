"use client";

import React, { useState } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Add01Icon,
  Search01Icon,
  Folder01Icon,
  ChevronDownIcon,
  SidebarLeft01Icon,
  ListFilterIcon,
  ArrowDown01Icon,
} from "@hugeicons/core-free-icons";
import Link from "next/link";
import SearchModal from "@/components/shared/Modal";

interface HistoryItem {
  id: string;
  title: string;
}

export default function Sidebar() {
  const [pinnedOpen, setPinnedOpen] = useState(true);
  const [chatsOpen, setChatsOpen] = useState(true);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const pinnedItems: HistoryItem[] = [
    {
      id: "pin-1",
      title: "The Black Dahlia murder case",
    },
  ];

  const recentChats: HistoryItem[] = [
    {
      id: "chat-1",
      title: "Training a model from scratch t...",
    },
  ];

  return (
    <>
      <aside className="w-75 px-3 h-screen flex flex-col bg-[#2a2929] text-white select-none border-r border-[#383838] font-mono text-[14px]">
        {/* Top Header / Logo */}
        <div className="pt-4 px-3 pb-1.5 flex items-center justify-between">
          <button
            type="button"
            className="flex items-center gap-2.5 py-1 rounded-xl hover:bg-[#222222] transition-colors text-white font-semibold text-[16px]"
          >
            <HugeiconsIcon icon={SidebarLeft01Icon} size={18} strokeWidth={2} />
            <span className="tracking-tight text-white">Tessa</span>
          </button>

          <button
            type="button"
            title="Collapse sidebar"
            className="p-1.5 text-white/70 hover:text-white hover:bg-[#222222] rounded-xl transition-colors"
          ></button>
        </div>

        {/* Primary Navigation List (Tight, clean spacing) */}
        <nav className="px-1 py-0.5 space-y-0.5">
          <Link
            type="button"
            href={"/new"}
            className="w-full flex items-center gap-3 px-1.5 py-1.5 rounded-xl text-white hover:bg-[#222222] transition-colors text-[14px]"
          >
            <HugeiconsIcon
              icon={Add01Icon}
              size={14}
              strokeWidth={2.4}
              className="text-white"
            />
            <span className="text-white">New</span>
          </Link>
          <button
            type="button"
            onClick={() => setIsSearchOpen(true)}
            className="w-full flex items-center gap-3 px-1.5 py-1.5 rounded-xl text-white hover:bg-[#222222] transition-colors text-[14px]"
          >
            <HugeiconsIcon
              icon={Search01Icon}
              size={18}
              strokeWidth={2}
              className="text-white shrink-0"
            />
            <span className="text-white">Search</span>
          </button>

          <Link
            href={"/projects"}
            type="button"
            className="w-full flex items-center gap-3 px-1.5 py-1.5 rounded-xl text-white hover:bg-[#222222] transition-colors text-[14px]"
          >
            <HugeiconsIcon
              icon={Folder01Icon}
              size={18}
              strokeWidth={2}
              className="text-white shrink-0"
            />
            <span className="text-white">Projects</span>
          </Link>
        </nav>

        {/* Scrollable Recents / Pinned section */}
        <div className="flex-1 overflow-y-auto px-1 py-2 mt-2 space-y-3">
          {/* Pinned Section */}
          <div>
            <button
              type="button"
              onClick={() => setPinnedOpen(!pinnedOpen)}
              className="flex items-center gap-1.5 px-2 py-0.5 text-[13px] font-semibold text-white/80 hover:text-white transition-colors"
            >
              <span>Pinned</span>
              <HugeiconsIcon
                icon={ChevronDownIcon}
                size={14}
                strokeWidth={2}
                className={`transition-transform duration-200 ${
                  pinnedOpen ? "rotate-0" : "-rotate-90"
                }`}
              />
            </button>

            {pinnedOpen && (
              <div className="mt-0.5 space-y-0.5">
                <Link
                  href="/projects/1"
                  className="flex items-center gap-2.5 px-2.5 py-1 text-[14px] text-white font-medium"
                >
                  <HugeiconsIcon
                    icon={Folder01Icon}
                    size={18}
                    strokeWidth={2}
                    className="text-white shrink-0"
                  />
                  <span className="truncate">Mysteries</span>
                </Link>

                <div className="pl-6 space-y-0.5">
                  {pinnedItems.map((item: { id: string; title: string }) => (
                    <Link
                      href={`/chats/${item.id}`}
                      key={item.id}
                      type="button"
                      className="w-full flex items-center gap-2.5 px-1 py-1 rounded-lg text-white/80 hover:text-white hover:bg-[#222222] transition-colors text-left"
                    >
                      <span className="w-2.5 h-2.5 rounded-full border border-white/60 shrink-0" />
                      <span className="truncate text-[15px]">{item.title}</span>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chats and tasks Section */}
          <div>
            <div className="flex items-center justify-between px-2 py-0.5">
              <button
                type="button"
                onClick={() => setChatsOpen(!chatsOpen)}
                className="flex items-center gap-1.5 text-[13px] font-semibold text-white/80 hover:text-white transition-colors"
              >
                <span>Chats</span>
                <HugeiconsIcon
                  icon={ArrowDown01Icon}
                  size={14}
                  strokeWidth={2}
                  className={`transition-transform duration-200 ${
                    chatsOpen ? "rotate-0" : "-rotate-90"
                  }`}
                />
              </button>

              <button
                type="button"
                title="Filter"
                className="p-1 text-white/70 hover:text-white hover:bg-[#222222] rounded-lg transition-colors"
              >
                <HugeiconsIcon icon={ListFilterIcon} size={15} strokeWidth={2} />
              </button>
            </div>

            {chatsOpen && (
              <div className="mt-0.5 space-y-0.5">
                {recentChats.map((item) => (
                  <Link
                    href={`/chats/${item.id}`}
                    key={item.id}
                    type="button"
                    className="w-full flex items-center gap-2.5 px-2.5 py-1 rounded-lg text-white/80 hover:text-white hover:bg-[#222222] transition-colors text-left"
                  >
                    <span className="w-2.5 h-2.5 rounded-full border border-white/60 shrink-0" />
                    <span className="truncate text-[15px]">{item.title}</span>
                  </Link>
                ))}

                <Link
                  type="button"
                  href={"/chats"}
                  className="w-full mt-2 text-left px-2.5 py-1 text-[13px] text-white/60 hover:text-white transition-colors font-medium"
                >
                  View all
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Profile Footer */}
        <div className="border-t border-[#393939] ">
          <button
            type="button"
            className="w-full flex items-center justify-between p-2 transition-colors text-left group"
          >
            <div className="flex items-center gap-2.5 min-w-0">
              {/* User Avatar */}
              <div className="w-8 h-8 rounded-full overflow-hidden bg-[#181818] shrink-0 flex items-center justify-center text-[13px] font-bold text-white border border-white/20">
                <span>K</span>
              </div>

              <div className="flex items-center gap-1.5 truncate text-[13px]">
                <span className="font-semibold text-white truncate">Krishna</span>
                <HugeiconsIcon
                  icon={ArrowDown01Icon}
                  size={14}
                  strokeWidth={2}
                  className="text-white/70"
                />
              </div>
            </div>
          </button>
        </div>
      </aside>

      {/* Global Search Modal */}
      <SearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
      />
    </>
  );
}
