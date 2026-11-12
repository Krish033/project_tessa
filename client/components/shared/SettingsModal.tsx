"use client";

import React, { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Search01Icon,
  Cancel01Icon,
  UserIcon,
  CreditCardIcon,
  Briefcase01Icon,
  Notification01Icon,
  FavouriteIcon,
  CodeXmlIcon,
  Copy01Icon,
  MoreHorizontalIcon,
  ChevronDownIcon,
  Grid2X2Icon,
  FileCodeIcon,
} from "@hugeicons/core-free-icons";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

interface SearchResultItem {
  id: string;
  title: string;
  subtitle?: string;
  tab: string;
  iconType: "account" | "appearance" | "claude" | "capabilities" | "notifications" | "privacy" | "billing" | "skills" | "connectors" | "plugins" | "customize" | "code";
}

const SETTINGS_SEARCH_ITEMS: SearchResultItem[] = [
  { id: "account", title: "Account", tab: "account", iconType: "account" },
  { id: "appearance", title: "Appearance", tab: "appearance", iconType: "appearance" },
  { id: "claude", title: "Your Claude", tab: "claude", iconType: "claude" },
  { id: "capabilities", title: "Capabilities", tab: "capabilities", iconType: "capabilities" },
  { id: "notifications", title: "Notifications", tab: "notifications", iconType: "notifications" },
  { id: "privacy", title: "Privacy", tab: "privacy", iconType: "privacy" },
  { id: "billing", title: "Billing", subtitle: "Your plan", tab: "billing", iconType: "billing" },
  { id: "skills", title: "Skills", subtitle: "skill-creator", tab: "capabilities", iconType: "skills" },
  { id: "connectors", title: "Connectors", subtitle: "integrations", tab: "capabilities", iconType: "connectors" },
  { id: "plugins", title: "Plugins", subtitle: "developer tools", tab: "code", iconType: "plugins" },
  { id: "customize", title: "Customize", tab: "customize", iconType: "customize" },
  { id: "code", title: "Code", tab: "code", iconType: "code" },
];

function highlightMatch(text: string, query: string) {
  if (!query) return <span>{text}</span>;

  // Case-insensitive match highlighting in blue (#60a5fa)
  const regex = new RegExp(`(${query.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&")})`, "gi");
  const parts = text.split(regex);

  return (
    <span>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <span key={i} className="text-[#60a5fa] font-semibold">
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  );
}

function renderSearchIcon(type: SearchResultItem["iconType"]) {
  switch (type) {
    case "account":
      return <HugeiconsIcon icon={UserIcon} size={15} strokeWidth={2} className="shrink-0 text-[#b5b5b5]" />;
    case "appearance":
      return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="shrink-0 text-[#b5b5b5]">
          <polygon points="4,4 20,20 4,20" />
        </svg>
      );
    case "claude":
      return (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="shrink-0 text-[#b5b5b5]">
          <path d="M12 2v20M2 12h20M5 5l14 14M19 5L5 19" />
        </svg>
      );
    case "capabilities":
      return <HugeiconsIcon icon={Briefcase01Icon} size={15} strokeWidth={1.8} className="shrink-0 text-[#b5b5b5]" />;
    case "notifications":
      return <HugeiconsIcon icon={Notification01Icon} size={15} strokeWidth={1.8} className="shrink-0 text-[#b5b5b5]" />;
    case "privacy":
      return (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0 text-[#b5b5b5]">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      );
    case "billing":
      return <HugeiconsIcon icon={CreditCardIcon} size={15} strokeWidth={1.8} className="shrink-0 text-[#b5b5b5]" />;
    case "skills":
      return <HugeiconsIcon icon={FileCodeIcon} size={15} strokeWidth={1.8} className="shrink-0 text-[#b5b5b5]" />;
    case "connectors":
      return <HugeiconsIcon icon={Grid2X2Icon} size={15} strokeWidth={1.8} className="shrink-0 text-[#b5b5b5]" />;
    case "plugins":
      return (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="shrink-0 text-[#b5b5b5]">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4" />
        </svg>
      );
    case "customize":
      return (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="shrink-0 text-[#b5b5b5]">
          <circle cx="6" cy="6" r="3" />
          <path d="M8.1 8.1L20 20" />
          <circle cx="18" cy="18" r="3" />
        </svg>
      );
    case "code":
      return <HugeiconsIcon icon={CodeXmlIcon} size={15} strokeWidth={1.8} className="shrink-0 text-[#b5b5b5]" />;
  }
}

export default function SettingsModal({
  isOpen,
  onClose,
  activeTab = "account",
  onTabChange,
}: SettingsModalProps) {
  const [copiedOrg, setCopiedOrg] = useState(false);
  const [currentTab, setCurrentTab] = useState(activeTab);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchDropdownOpen, setIsSearchDropdownOpen] = useState(false);
  const [selectedSearchIndex, setSelectedSearchIndex] = useState(3); // Default highlighted: Capabilities in screenshot
  const [workDescription, setWorkDescription] = useState("Software engineer");

  const searchContainerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setCurrentTab(activeTab);
  }, [activeTab]);

  useEffect(() => {
    if (isOpen) {
      setSearchQuery("");
      setIsSearchDropdownOpen(false);
    }
  }, [isOpen]);

  // Filter items based on searchQuery
  const searchResults = SETTINGS_SEARCH_ITEMS.filter((item) => {
    if (!searchQuery.trim()) return false;
    const q = searchQuery.toLowerCase();
    return (
      item.title.toLowerCase().includes(q) ||
      (item.subtitle && item.subtitle.toLowerCase().includes(q))
    );
  });

  // Handle Tab Click
  const handleTabSelect = (tabId: string) => {
    setCurrentTab(tabId);
    onTabChange?.(tabId);
    setIsSearchDropdownOpen(false);
    setSearchQuery("");
  };

  // Close search dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(e.target as Node)
      ) {
        setIsSearchDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Keyboard navigation & Esc in search
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        if (isSearchDropdownOpen) {
          setIsSearchDropdownOpen(false);
        } else {
          onClose();
        }
      } else if (isSearchDropdownOpen && searchResults.length > 0) {
        if (e.key === "ArrowDown") {
          e.preventDefault();
          setSelectedSearchIndex((prev) =>
            prev < searchResults.length - 1 ? prev + 1 : 0
          );
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          setSelectedSearchIndex((prev) =>
            prev > 0 ? prev - 1 : searchResults.length - 1
          );
        } else if (e.key === "Enter") {
          e.preventDefault();
          const target = searchResults[selectedSearchIndex];
          if (target) {
            handleTabSelect(target.tab);
          }
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, isSearchDropdownOpen, searchResults, selectedSearchIndex, onClose]);

  if (!isOpen) return null;

  const orgId = "40b46d3b-1979-44bc-80c6-59a02c26eb3c";

  const handleCopyOrg = () => {
    navigator.clipboard?.writeText(orgId);
    setCopiedOrg(true);
    setTimeout(() => setCopiedOrg(false), 2000);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Settings"
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/65 backdrop-blur-[2px] animate-in fade-in duration-150 select-none font-mono"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-[960px] h-[92vh] max-h-[640px] bg-[#1a1a1a] text-[#ededed] rounded-2xl shadow-[0_24px_60px_rgba(0,0,0,0.85)] border border-[#2d2d2d] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150">
        {/* Top Header */}
        <div className="h-12 px-5 flex items-center justify-between border-b border-[#282828] shrink-0">
          <span className="text-[14px] font-medium text-[#f0f0f0]">Settings</span>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-[#888888] hover:text-white rounded-lg hover:bg-[#282828] transition-colors cursor-pointer"
            aria-label="Close"
          >
            <HugeiconsIcon icon={Cancel01Icon} size={16} strokeWidth={2} />
          </button>
        </div>

        {/* Modal Body: Sidebar + Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Settings Left Navigation Sidebar */}
          <div className="w-[210px] shrink-0 border-r border-[#282828] p-3 flex flex-col space-y-4 relative">
            {/* Search Input Container */}
            <div ref={searchContainerRef} className="relative z-20">
              <div
                className={`relative flex items-center h-8 bg-[#202020] border rounded-lg transition-all ${
                  isSearchDropdownOpen
                    ? "border-[#2563eb] ring-2 ring-[#2563eb]/20"
                    : "border-[#2f2f2f] hover:border-[#3d3d3d]"
                }`}
              >
                <HugeiconsIcon
                  icon={Search01Icon}
                  size={14}
                  strokeWidth={2}
                  className="absolute left-2.5 text-[#707070]"
                />
                <input
                  ref={searchInputRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setIsSearchDropdownOpen(e.target.value.trim().length > 0);
                    setSelectedSearchIndex(0);
                  }}
                  onFocus={() => {
                    if (searchQuery.trim().length > 0) {
                      setIsSearchDropdownOpen(true);
                    }
                  }}
                  placeholder="Search"
                  className="w-full h-full pl-8 pr-2.5 bg-transparent text-[12.5px] text-[#e0e0e0] placeholder-[#707070] outline-none"
                />
              </div>

              {/* Floating Search Dropdown Overlay */}
              {isSearchDropdownOpen && searchResults.length > 0 && (
                <div className="absolute left-0 top-full mt-1.5 w-[250px] max-h-[380px] overflow-y-auto bg-[#2b2b2b] border border-[#383838] rounded-2xl p-1.5 shadow-[0_20px_50px_rgba(0,0,0,0.95)] z-50 animate-in fade-in zoom-in-95 duration-100 select-none">
                  {searchResults.map((item, index) => {
                    const isSelected = index === selectedSearchIndex;
                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => handleTabSelect(item.tab)}
                        onMouseEnter={() => setSelectedSearchIndex(index)}
                        className={`w-full flex items-start gap-2.5 px-3 py-2 rounded-xl transition-all text-left cursor-pointer ${
                          isSelected
                            ? "bg-[#424242] text-white shadow-sm"
                            : "hover:bg-[#353535] text-[#d6d6d6]"
                        }`}
                      >
                        <div className="mt-0.5 shrink-0">
                          {renderSearchIcon(item.iconType)}
                        </div>

                        <div className="flex flex-col min-w-0">
                          <span className="text-[13px] font-normal leading-tight">
                            {highlightMatch(item.title, searchQuery)}
                          </span>
                          {item.subtitle && (
                            <span className="text-[11px] text-[#8e8e8e] mt-0.5 leading-tight">
                              {highlightMatch(item.subtitle, searchQuery)}
                            </span>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Scrollable Navigation Items */}
            <div className="flex-1 overflow-y-auto space-y-4 -mr-1 pr-1">
              {/* Section 1: Account & Billing */}
              <div className="space-y-0.5">
                <button
                  type="button"
                  onClick={() => handleTabSelect("account")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "account"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <HugeiconsIcon icon={UserIcon} size={15} strokeWidth={2} />
                  <span>Account</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleTabSelect("billing")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "billing"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <HugeiconsIcon icon={CreditCardIcon} size={15} strokeWidth={1.8} />
                  <span>Billing</span>
                </button>
              </div>

              {/* Subtle Divider */}
              <div className="h-[1px] bg-[#272727] mx-1" />

              {/* Section 2: Appearance, Claude, Capabilities, Notifications, Privacy, Wellbeing */}
              <div className="space-y-0.5">
                <button
                  type="button"
                  onClick={() => handleTabSelect("appearance")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "appearance"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="shrink-0"
                  >
                    <polygon points="4,4 20,20 4,20" />
                  </svg>
                  <span>Appearance</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleTabSelect("claude")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "claude"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    className="shrink-0"
                  >
                    <path d="M12 2v20M2 12h20M5 5l14 14M19 5L5 19" />
                  </svg>
                  <span className="truncate">Your Claude</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleTabSelect("capabilities")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "capabilities"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <HugeiconsIcon icon={Briefcase01Icon} size={15} strokeWidth={1.8} />
                  <span>Capabilities</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleTabSelect("notifications")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "notifications"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <HugeiconsIcon icon={Notification01Icon} size={15} strokeWidth={1.8} />
                  <span>Notifications</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleTabSelect("privacy")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "privacy"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  </svg>
                  <span>Privacy</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleTabSelect("wellbeing")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "wellbeing"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <HugeiconsIcon icon={FavouriteIcon} size={15} strokeWidth={1.8} />
                  <span>Wellbeing</span>
                </button>
              </div>

              {/* Subtle Divider */}
              <div className="h-[1px] bg-[#272727] mx-1" />

              {/* Section 3: Customize & Code */}
              <div className="space-y-0.5">
                <button
                  type="button"
                  onClick={() => handleTabSelect("customize")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "customize"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <svg
                    width="15"
                    height="15"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  >
                    <circle cx="6" cy="6" r="3" />
                    <path d="M8.1 8.1L20 20" />
                    <circle cx="18" cy="18" r="3" />
                  </svg>
                  <span>Customize</span>
                </button>

                <button
                  type="button"
                  onClick={() => handleTabSelect("code")}
                  className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium transition-colors cursor-pointer ${
                    currentTab === "code"
                      ? "bg-[#303030] text-white"
                      : "text-[#a0a0a0] hover:text-white hover:bg-[#242424]"
                  }`}
                >
                  <HugeiconsIcon icon={CodeXmlIcon} size={15} strokeWidth={1.8} />
                  <span>Code</span>
                </button>
              </div>
            </div>
          </div>

          {/* Right Main Content Pane */}
          <div className="flex-1 p-6 md:p-8 overflow-y-auto space-y-7">
            {currentTab === "account" ? (
              <>
                {/* Profile Section */}
                <div className="space-y-4">
                  <h3 className="text-[15px] font-semibold text-[#f0f0f0] tracking-tight">
                    Profile
                  </h3>

                  {/* Profile Photo */}
                  <div className="flex items-center justify-between pb-1">
                    <div>
                      <div className="text-[13px] font-medium text-[#ededed]">
                        Profile photo
                      </div>
                      <div className="text-[11.5px] text-[#7a7a7a]">
                        PNG, JPEG, or WebP, up to 10MB.
                      </div>
                    </div>
                    <div className="w-9 h-9 rounded-full overflow-hidden border border-[#383838] relative shrink-0">
                      <Image
                        src="/avatar.png"
                        alt="Profile"
                        width={36}
                        height={36}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>

                  {/* Full Name */}
                  <div className="flex items-center justify-between gap-4">
                    <label className="text-[13px] font-normal text-[#d4d4d4] shrink-0">
                      Full name
                    </label>
                    <input
                      type="text"
                      defaultValue="Sri Krishna"
                      className="w-full max-w-[280px] h-9 px-3 bg-[#242424] border border-[#333333] focus:border-[#505050] rounded-xl text-[13px] text-[#f0f0f0] outline-none"
                    />
                  </div>

                  {/* What should Claude call you? */}
                  <div className="flex items-center justify-between gap-4">
                    <label className="text-[13px] font-normal text-[#d4d4d4] shrink-0">
                      What should Claude call you?
                    </label>
                    <input
                      type="text"
                      defaultValue="Krishna"
                      className="w-full max-w-[280px] h-9 px-3 bg-[#242424] border border-[#333333] focus:border-[#505050] rounded-xl text-[13px] text-[#f0f0f0] outline-none"
                    />
                  </div>

                  {/* What best describes your work? */}
                  <div className="flex items-center justify-between gap-4">
                    <label className="text-[13px] font-normal text-[#d4d4d4] shrink-0">
                      What best describes your work?
                    </label>
                    <div className="relative w-full max-w-[280px]">
                      <select
                        value={workDescription}
                        onChange={(e) => setWorkDescription(e.target.value)}
                        className="w-full h-9 pl-3 pr-8 bg-[#242424] border border-[#333333] focus:border-[#505050] rounded-xl text-[13px] text-[#f0f0f0] outline-none appearance-none cursor-pointer"
                      >
                        <option value="Software engineer">Software engineer</option>
                        <option value="Designer">Designer</option>
                        <option value="Product manager">Product manager</option>
                        <option value="Researcher">Researcher</option>
                        <option value="Student">Student</option>
                        <option value="Other">Other</option>
                      </select>
                      <HugeiconsIcon
                        icon={ChevronDownIcon}
                        size={14}
                        strokeWidth={2}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[#888888] pointer-events-none"
                      />
                    </div>
                  </div>

                  {/* Organization ID */}
                  <div className="flex items-center justify-between gap-4 pt-1">
                    <span className="text-[13px] font-normal text-[#d4d4d4]">
                      Organization ID
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-[12px] font-mono text-[#8c8c8c]">
                        {orgId}
                      </span>
                      <button
                        type="button"
                        onClick={handleCopyOrg}
                        title="Copy Organization ID"
                        className="p-1 text-[#888888] hover:text-white rounded hover:bg-[#2c2c2c] transition-colors cursor-pointer"
                      >
                        <HugeiconsIcon icon={Copy01Icon} size={14} strokeWidth={2} />
                      </button>
                      {copiedOrg && (
                        <span className="text-[11px] text-green-400 font-mono">
                          Copied
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Where you're logged in */}
                <div className="space-y-3 pt-3 border-t border-[#262626]">
                  <div className="flex items-center justify-between">
                    <h3 className="text-[15px] font-semibold text-[#f0f0f0] tracking-tight">
                      Where you’re logged in
                    </h3>
                    <button
                      type="button"
                      className="px-3 py-1.5 rounded-xl bg-[#2b2b2b] hover:bg-[#343434] text-[12px] font-medium text-[#e0e0e0] transition-colors cursor-pointer"
                    >
                      Log out of all devices
                    </button>
                  </div>

                  {/* Sessions Table / List */}
                  <div className="w-full text-[12px]">
                    <div className="grid grid-cols-12 text-[#787878] pb-2 px-2 text-[11.5px] border-b border-[#252525]">
                      <span className="col-span-3">Device</span>
                      <span className="col-span-3">Location</span>
                      <span className="col-span-3">Signed in</span>
                      <span className="col-span-3 text-right">Last active</span>
                    </div>

                    {/* Session Row 1: Android */}
                    <div className="grid grid-cols-12 items-center py-2.5 px-2 hover:bg-[#222222] rounded-xl transition-colors text-[#cccccc]">
                      <div className="col-span-3 font-medium text-[#f0f0f0]">
                        Android (Android)
                      </div>
                      <div className="col-span-3 truncate text-[#999999]">
                        Coimbatore, Tamil Nadu,...
                      </div>
                      <div className="col-span-3 text-[#999999]">
                        Nov 5, 2026, 9:35 AM
                      </div>
                      <div className="col-span-3 flex items-center justify-end gap-1 text-[#999999]">
                        <span>Nov 11, 2026, 9:35 P</span>
                        <button
                          type="button"
                          className="p-1 hover:text-white rounded hover:bg-[#2e2e2e]"
                        >
                          <HugeiconsIcon icon={MoreHorizontalIcon} size={14} />
                        </button>
                      </div>
                    </div>

                    {/* Session Row 2: Firefox (Current) */}
                    <div className="grid grid-cols-12 items-center py-2.5 px-2 hover:bg-[#222222] rounded-xl transition-colors text-[#cccccc]">
                      <div className="col-span-3 font-medium text-[#f0f0f0] flex items-center gap-1.5">
                        <span className="truncate">Firefox (Wi...</span>
                        <span className="px-1.5 py-0.5 rounded-full bg-[#1e344e] text-[#60a5fa] text-[10px] font-medium">
                          Current
                        </span>
                      </div>
                      <div className="col-span-3 truncate text-[#999999]">
                        Coimbatore, Tamil Nadu,...
                      </div>
                      <div className="col-span-3 text-[#999999]">
                        Nov 4, 2026, 6:26 AM
                      </div>
                      <div className="col-span-3 text-right text-[#999999] pr-5">
                        Nov 12, 2026, 5:43 A
                      </div>
                    </div>
                  </div>
                </div>

                {/* Trusted Devices Section */}
                <div className="space-y-2 pt-3 border-t border-[#262626]">
                  <h3 className="text-[15px] font-semibold text-[#f0f0f0] tracking-tight">
                    Trusted devices
                  </h3>
                  <p className="text-[12px] text-[#7a7a7a]">
                    Devices that can control your computer remotely.
                  </p>
                  <div className="pt-2 text-[12.5px] text-[#909090]">
                    No trusted devices.
                  </div>
                </div>
              </>
            ) : (
              /* Other Tabs Placeholder */
              <div className="h-full flex flex-col items-center justify-center text-center py-16 text-[#7a7a7a]">
                <span className="text-[15px] font-semibold text-[#d0d0d0] capitalize mb-1">
                  {currentTab}
                </span>
                <p className="text-[12.5px]">
                  Settings for {currentTab} will appear here.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
