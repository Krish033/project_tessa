"use client";

import React, { useState, useEffect, useRef } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Cancel01Icon,
  Comment01Icon,
  Folder01Icon,
  BubbleChatAddIcon,
  MoreHorizontalIcon,
  CornerDownLeftIcon,
} from "@hugeicons/core-free-icons";
import { useRouter } from "next/navigation";

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type FilterCategory =
  | "All"
  | "Artifacts"
  | "Chats"
  | "Projects"
  | "Sessions"
  | "Tasks"
  | "Scheduled";

interface RecentItem {
  id: string;
  title: string;
  type: "chat" | "project";
  category: FilterCategory;
  href: string;
}

const CATEGORIES: FilterCategory[] = [
  "All",
  "Artifacts",
  "Chats",
  "Projects",
  "Sessions",
  "Tasks",
  "Scheduled",
];

const RECENT_ITEMS: RecentItem[] = [
  {
    id: "item-1",
    title: "Attaching images to Google Calendar",
    type: "chat",
    category: "Chats",
    href: "/chats/item-1",
  },
  {
    id: "item-2",
    title: "Calendar and post issues",
    type: "chat",
    category: "Chats",
    href: "/chats/item-2",
  },
  {
    id: "item-3",
    title: "Broward Partnership for kids",
    type: "project",
    category: "Projects",
    href: "/projects/broward",
  },
  {
    id: "item-4",
    title: "Covert browser monitoring via screenshots",
    type: "chat",
    category: "Chats",
    href: "/chats/item-4",
  },
  {
    id: "item-5",
    title: "Training a model from scratch timeline",
    type: "chat",
    category: "Chats",
    href: "/chats/training-model",
  },
  {
    id: "item-6",
    title: "The Black Dahlia murder case",
    type: "chat",
    category: "Chats",
    href: "/chats/black-dahlia",
  },
  {
    id: "item-7",
    title: "Mysteries",
    type: "project",
    category: "Projects",
    href: "/projects/1",
  },
];

export default function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<FilterCategory>("All");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input on open
  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setSelectedIndex(0);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    }
  }, [isOpen]);

  // Filter items based on query & category
  const filteredItems = RECENT_ITEMS.filter((item) => {
    const matchesCategory =
      activeCategory === "All" || item.category === activeCategory;
    const matchesQuery = item.title
      .toLowerCase()
      .includes(query.trim().toLowerCase());
    return matchesCategory && matchesQuery;
  });

  // Keyboard navigation & Shortcuts (Esc, Arrow keys, Enter, Tab)
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < filteredItems.length - 1 ? prev + 1 : 0
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : Math.max(0, filteredItems.length - 1)
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (filteredItems[selectedIndex]) {
          router.push(filteredItems[selectedIndex].href);
          onClose();
        }
      } else if (e.key === "Tab") {
        e.preventDefault();
        router.push("/new");
        onClose();
      } else if (e.key === "/") {
        // Toggle next filter category if input is not focused
        if (document.activeElement !== inputRef.current) {
          e.preventDefault();
          inputRef.current?.focus();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, selectedIndex, filteredItems, onClose, router]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-[2px] animate-in fade-in duration-150 font-mono select-none">
      {/* Backdrop overlay dismiss */}
      <div className="absolute inset-0" onClick={onClose} />

      {/* Modal Dialog Card */}
      <div className="relative w-full max-w-[620px] bg-[#222222] border border-[#333333] rounded-[24px] shadow-2xl overflow-hidden flex flex-col text-white">
        {/* Top Header / Search Input */}
        <div className="relative flex items-center justify-between px-6 pt-5 pb-3">
          <div className="flex-1 flex items-center">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setSelectedIndex(0);
              }}
              placeholder="Search"
              className="w-full bg-transparent border-none outline-none text-[17px] text-[#f0f0f0] placeholder-[#777777] font-mono tracking-tight"
            />
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1 text-[#888888] hover:text-white rounded-lg transition-colors ml-3"
            title="Close"
          >
            <HugeiconsIcon icon={Cancel01Icon} size={18} strokeWidth={2} />
          </button>
        </div>

        {/* Filter Pills List */}
        <div className="px-6 pb-4 flex items-center gap-1.5 overflow-x-auto no-scrollbar">
          {CATEGORIES.map((cat) => {
            const isActive = activeCategory === cat;
            return (
              <button
                key={cat}
                type="button"
                onClick={() => {
                  setActiveCategory(cat);
                  setSelectedIndex(0);
                }}
                className={`px-3 py-1 rounded-lg text-[13px] font-medium transition-colors ${
                  isActive
                    ? "bg-[#333333] text-white"
                    : "text-[#959595] hover:text-white hover:bg-[#282828]"
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>

        {/* Content Body */}
        <div className="px-4 py-2 max-h-[360px] overflow-y-auto space-y-4">
          {/* Recents Group */}
          <div>
            <div className="px-3 pb-1 text-[12px] text-[#777777] font-medium">
              Recents
            </div>

            <div className="space-y-0.5">
              {filteredItems.length === 0 ? (
                <div className="px-3 py-6 text-center text-[#777777] text-[13px]">
                  No results found for &ldquo;{query}&rdquo;
                </div>
              ) : (
                filteredItems.map((item, idx) => {
                  const isSelected = idx === selectedIndex;
                  return (
                    <div
                      key={item.id}
                      onClick={() => {
                        router.push(item.href);
                        onClose();
                      }}
                      onMouseEnter={() => setSelectedIndex(idx)}
                      className={`group flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer transition-colors ${
                        isSelected
                          ? "bg-[#333333] text-white"
                          : "text-[#cccccc] hover:bg-[#2a2a2a] hover:text-white"
                      }`}
                    >
                      <div className="flex items-center gap-3 min-w-0 pr-3">
                        <span className="shrink-0 text-[#888888] group-hover:text-white">
                          {item.type === "chat" ? (
                            <HugeiconsIcon
                              icon={Comment01Icon}
                              size={16}
                              strokeWidth={2}
                            />
                          ) : (
                            <HugeiconsIcon
                              icon={Folder01Icon}
                              size={16}
                              strokeWidth={2}
                            />
                          )}
                        </span>
                        <span className="truncate text-[13.5px]">
                          {item.title}
                        </span>
                      </div>

                      {/* Right action indicators on hover/selected */}
                      {isSelected ? (
                        <div className="flex items-center gap-2 text-[#999999]">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                            }}
                            className="p-0.5 hover:text-white"
                            title="More options"
                          >
                            <HugeiconsIcon
                              icon={MoreHorizontalIcon}
                              size={15}
                              strokeWidth={2}
                            />
                          </button>
                          <HugeiconsIcon
                            icon={CornerDownLeftIcon}
                            size={14}
                            strokeWidth={2}
                            className="text-[#888888]"
                          />
                        </div>
                      ) : null}
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Actions Group */}
          <div>
            <div className="px-3 pb-1 text-[12px] text-[#777777] font-medium">
              Actions
            </div>

            <div
              onClick={() => {
                router.push("/new");
                onClose();
              }}
              className="group flex items-center gap-3 px-3 py-2 rounded-xl text-[#cccccc] hover:bg-[#2a2a2a] hover:text-white cursor-pointer transition-colors"
            >
              <HugeiconsIcon
                icon={BubbleChatAddIcon}
                size={16}
                strokeWidth={2}
                className="text-[#888888] group-hover:text-white"
              />
              <span className="text-[13.5px]">New chat</span>
            </div>
          </div>
        </div>

        {/* Footer / Shortcut Legends */}
        <div className="px-5 py-3 border-t border-[#2d2d2d] bg-[#1d1d1d] flex items-center justify-between text-[11px] text-[#777777]">
          {/* Left shortcuts */}
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5">
              <span>Close</span>
              <kbd className="px-1.5 py-0.5 rounded bg-[#2a2a2a] border border-[#383838] text-[#aaaaaa]">
                Esc
              </kbd>
            </span>

            <span className="flex items-center gap-1.5">
              <span>Change type</span>
              <kbd className="px-1.5 py-0.5 rounded bg-[#2a2a2a] border border-[#383838] text-[#aaaaaa]">
                ← →
              </kbd>
            </span>

            <span className="flex items-center gap-1.5">
              <span>Filters</span>
              <kbd className="px-1.5 py-0.5 rounded bg-[#2a2a2a] border border-[#383838] text-[#aaaaaa]">
                /
              </kbd>
            </span>

            <span className="flex items-center gap-1.5">
              <span>Actions</span>
              <kbd className="px-1.5 py-0.5 rounded bg-[#2a2a2a] border border-[#383838] text-[#aaaaaa]">
                Alt ↵
              </kbd>
            </span>
          </div>

          {/* Right compose shortcut */}
          <div className="flex items-center gap-1.5">
            <span>Compose</span>
            <kbd className="px-1.5 py-0.5 rounded bg-[#2a2a2a] border border-[#383838] text-[#aaaaaa]">
              Tab
            </kbd>
          </div>
        </div>
      </div>
    </div>
  );
}
