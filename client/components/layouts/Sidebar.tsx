"use client";

import React, { useState } from "react";
import Image from "next/image";
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
import { useRouter, usePathname } from "next/navigation";
import SearchModal from "@/components/shared/Modal";
import ProfileDropdown from "@/components/shared/ProfileDropdown";
import CreateProjectModal from "@/components/shared/CreateProjectModal";
import SettingsModal from "@/components/shared/SettingsModal";

interface HistoryItem {
  id: string;
  title: string;
}

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const [pinnedOpen, setPinnedOpen] = useState(true);
  const [mysteriesOpen, setMysteriesOpen] = useState(true);
  const [chatsOpen, setChatsOpen] = useState(true);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isCreateProjectOpen, setIsCreateProjectOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [settingsTab, setSettingsTab] = useState("account");

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

  // Global keyboard shortcuts:
  // 1. Ctrl+Shift+K to open Search modal
  // 2. Ctrl+Shift+, to open Settings modal
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey) {
        if (e.key === "K" || e.key === "k") {
          e.preventDefault();
          setIsSearchOpen(true);
        } else if (e.key === "," || e.key === "<") {
          e.preventDefault();
          openSettings("account");
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Listen to hash changes in URL (e.g. #settings/account)
  React.useEffect(() => {
    const checkHash = () => {
      const hash = window.location.hash;
      if (hash.startsWith("#settings")) {
        const parts = hash.replace("#settings", "").split("/").filter(Boolean);
        const tab = parts[0] || "account";
        setSettingsTab(tab);
        setIsSettingsOpen(true);
      } else {
        setIsSettingsOpen(false);
      }
    };

    checkHash();
    window.addEventListener("hashchange", checkHash);
    return () => window.removeEventListener("hashchange", checkHash);
  }, []);

  const openSettings = (tab: string = "account") => {
    setSettingsTab(tab);
    setIsSettingsOpen(true);
    window.location.hash = `#settings/${tab}`;
  };

  const closeSettings = () => {
    setIsSettingsOpen(false);
    if (window.location.hash.startsWith("#settings")) {
      window.history.pushState(
        "",
        document.title,
        window.location.pathname + window.location.search
      );
    }
  };

  const handleSettingsTabChange = (tab: string) => {
    setSettingsTab(tab);
    window.location.hash = `#settings/${tab}`;
  };

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
            className={`w-full flex items-center gap-3 px-2 py-1.5 rounded-xl transition-colors text-[14px] ${
              pathname === "/new" || pathname === "/"
                ? "bg-[#383737] text-white font-medium"
                : "text-white/80 hover:text-white hover:bg-[#222222]"
            }`}
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
            className="w-full flex items-center gap-3 px-2 py-1.5 rounded-xl text-white/80 hover:text-white hover:bg-[#222222] transition-colors text-[14px] cursor-pointer"
          >
            <HugeiconsIcon
              icon={Search01Icon}
              size={18}
              strokeWidth={2}
              className="text-white shrink-0"
            />
            <span className="text-white">Search</span>
          </button>

          <div className="relative group/projects">
            <Link
              href={"/projects"}
              type="button"
              className={`w-full flex items-center justify-between px-2 py-1.5 rounded-xl transition-colors text-[14px] ${
                pathname === "/projects"
                  ? "bg-[#383737] text-white font-medium"
                  : "text-white/80 hover:text-white hover:bg-[#222222]"
              }`}
            >
              <div className="flex items-center gap-3">
                <HugeiconsIcon
                  icon={Folder01Icon}
                  size={18}
                  strokeWidth={2}
                  className="text-white shrink-0"
                />
                <span className="text-white">Projects</span>
              </div>
            </Link>

            {/* Plus button appearing on hover */}
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setIsCreateProjectOpen(true);
              }}
              title="Create a project"
              className="absolute right-2 top-1/2 -translate-y-1/2 w-5 h-5 flex items-center justify-center rounded-md text-[#999999] hover:text-white hover:bg-[#333333] opacity-0 group-hover/projects:opacity-100 transition-all cursor-pointer"
            >
              <HugeiconsIcon
                icon={Add01Icon}
                size={14}
                strokeWidth={2.4}
              />
            </button>
          </div>
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
                <div
                  className={`flex items-center gap-2.5 px-2.5 py-1 text-[14px] font-medium rounded-lg transition-colors group/mysteries ${
                    pathname.startsWith("/projects/1") || pathname.startsWith("/projects/mysteries")
                      ? "bg-[#383737] text-white"
                      : "text-white/80 hover:text-white hover:bg-[#222222]"
                  }`}
                >
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setMysteriesOpen(!mysteriesOpen);
                    }}
                    title={mysteriesOpen ? "Collapse folder" : "Expand folder"}
                    className="p-0.5 text-white/80 hover:text-white rounded transition-transform cursor-pointer"
                  >
                    <HugeiconsIcon
                      icon={Folder01Icon}
                      size={18}
                      strokeWidth={2}
                      className="text-white shrink-0"
                    />
                  </button>

                  <Link
                    href="/projects/1"
                    className="truncate flex-1 hover:text-white text-white/90"
                  >
                    Mysteries
                  </Link>
                </div>

                {mysteriesOpen && (
                  <div className="pl-6 space-y-0.5 animate-in fade-in duration-150">
                    {pinnedItems.map((item: { id: string; title: string }) => {
                      const isActive =
                        pathname === `/chats/${item.id}` ||
                        pathname.endsWith(item.id);
                      return (
                        <Link
                          href={`/chats/${item.id}`}
                          key={item.id}
                          type="button"
                          className={`w-full flex items-center gap-2.5 px-2 py-1 rounded-lg transition-colors text-left ${
                            isActive
                              ? "bg-[#383737] text-white font-medium"
                              : "text-white/80 hover:text-white hover:bg-[#222222]"
                          }`}
                        >
                          <span
                            className={`w-2 h-2 rounded-full border shrink-0 ${
                              isActive ? "border-white bg-white" : "border-white/60"
                            }`}
                          />
                          <span className="truncate text-[14px]">{item.title}</span>
                        </Link>
                      );
                    })}
                  </div>
                )}
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
                {recentChats.map((item) => {
                  const isActive =
                    pathname === `/chats/${item.id}` ||
                    pathname.endsWith(item.id);
                  return (
                    <Link
                      href={`/chats/${item.id}`}
                      key={item.id}
                      type="button"
                      className={`w-full flex items-center gap-2.5 px-2.5 py-1 rounded-lg transition-colors text-left ${
                        isActive
                          ? "bg-[#383737] text-white font-medium"
                          : "text-white/80 hover:text-white hover:bg-[#222222]"
                      }`}
                    >
                      <span
                        className={`w-2.5 h-2.5 rounded-full border shrink-0 ${
                          isActive ? "border-white bg-white" : "border-white/60"
                        }`}
                      />
                      <span className="truncate text-[14px]">{item.title}</span>
                    </Link>
                  );
                })}

                <Link
                  type="button"
                  href={"/chats"}
                  className={`w-full mt-2 text-left px-2.5 py-1 text-[13px] rounded-lg transition-colors font-medium ${
                    pathname === "/chats"
                      ? "bg-[#383737] text-white"
                      : "text-white/60 hover:text-white hover:bg-[#222222]"
                  }`}
                >
                  View all
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Profile Footer */}
        <div className="relative border-t border-[#393939] pt-1">
          {/* Profile Dropdown Popup */}
          <ProfileDropdown
            isOpen={isProfileOpen}
            onClose={() => setIsProfileOpen(false)}
            email="srik51977@gmail.com"
            onOpenSettings={() => openSettings("account")}
          />

          <div className="flex items-center justify-between px-1 py-1">
            <button
              type="button"
              onClick={() => setIsProfileOpen((prev) => !prev)}
              className="flex items-center gap-2 px-2 py-1.5 rounded-xl hover:bg-[#383838] transition-colors text-left group min-w-0 cursor-pointer"
            >
              {/* User Avatar */}
              <div className="w-6 h-6 rounded-full overflow-hidden bg-[#181818] shrink-0 border border-white/20 relative">
                <Image
                  src="/avatar.png"
                  alt="Krishna"
                  width={24}
                  height={24}
                  className="w-full h-full object-cover"
                />
              </div>

              <div className="flex items-center gap-1.5 truncate text-[13px] text-[#ededed]">
                <span className="font-semibold text-white">Krishna</span>
                <span className="text-[#888888] font-normal">· Free</span>
                <HugeiconsIcon
                  icon={ArrowDown01Icon}
                  size={13}
                  strokeWidth={2}
                  className={`text-[#888888] transition-transform duration-150 ${
                    isProfileOpen ? "rotate-180" : ""
                  }`}
                />
              </div>
            </button>

            {/* Right side icon: devices / app icon button */}
            <button
              type="button"
              title="Get apps and extensions"
              className="p-1.5 text-[#888888] hover:text-white hover:bg-[#383838] rounded-lg transition-colors cursor-pointer"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Z" />
                <path d="M8 20h8M12 16v4" />
                <rect x="15" y="11" width="6" height="9" rx="1.2" fill="#2a2929" />
                <rect x="15" y="11" width="6" height="9" rx="1.2" />
              </svg>
            </button>
          </div>
        </div>
      </aside>

      {/* Global Search Modal */}
      <SearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
      />

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={isCreateProjectOpen}
        onClose={() => setIsCreateProjectOpen(false)}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={closeSettings}
        activeTab={settingsTab}
        onTabChange={handleSettingsTabChange}
      />
    </>
  );
}
