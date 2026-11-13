"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Search01Icon,
  ListFilterIcon,
} from "@hugeicons/core-free-icons";
import { useChats, useCreateChat } from "@/lib/hooks";

export default function ChatsPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const { data: chats = [], isLoading } = useChats();
  const createChatMutation = useCreateChat();

  const handleCreateNew = async () => {
    try {
      const newChat = await createChatMutation.mutateAsync({ title: "New Conversation" });
      router.push(`/chats/${newChat.id}`);
    } catch (err) {
      console.error("Failed to create chat", err);
    }
  };

  const filteredChats = chats.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-full flex-1 bg-[#141414] text-white font-mono select-none px-8 py-7 md:px-14 md:py-9 overflow-y-auto">
      {/* Top Header Section */}
      <div className="flex items-center justify-between pb-8">
        <h1 className="text-[26px] md:text-[28px] font-semibold text-white tracking-tight">
          Chats and tasks
        </h1>

        {/* Right Action Bar */}
        <div className="flex items-center gap-3">
          {/* Search Icon */}
          <button
            type="button"
            className="p-1.5 text-[#949494] hover:text-white transition-colors"
            title="Search chats"
          >
            <HugeiconsIcon icon={Search01Icon} size={18} strokeWidth={2} />
          </button>

          {/* Filter Icon */}
          <button
            type="button"
            className="p-1.5 text-[#949494] hover:text-white transition-colors mr-1"
            title="Filter chats"
          >
            <HugeiconsIcon icon={ListFilterIcon} size={18} strokeWidth={2} />
          </button>

          {/* Select Button */}
          <button
            type="button"
            className="px-3.5 py-1.5 rounded-xl bg-[#262626] hover:bg-[#303030] border border-[#333333] text-[#e0e0e0] hover:text-white text-[13px] font-medium tracking-tight transition-colors shadow-sm"
          >
            Select
          </button>

          {/* New Button */}
          <button
            type="button"
            onClick={handleCreateNew}
            className="px-3.5 py-1.5 rounded-xl bg-white hover:bg-[#eaeaea] text-black text-[13px] font-medium tracking-tight transition-colors shadow-sm cursor-pointer"
          >
            New
          </button>
        </div>
      </div>

      {/* Chats and Tasks List */}
      {isLoading ? (
        <div className="text-[#888888] text-[14px]">Loading chats...</div>
      ) : filteredChats.length === 0 ? (
        <div className="text-[#666666] text-[14px]">No chats found. Click &quot;New&quot; to start a conversation.</div>
      ) : (
        <div className="divide-y divide-[#222222]">
          {filteredChats.map((chat) => (
            <Link
              key={chat.id}
              href={`/chats/${chat.id}`}
              className="flex items-center justify-between py-4 px-2 hover:bg-[#1a1a1a] rounded-xl transition-colors group"
            >
              <span className="text-[14px] text-[#e8e8e8] group-hover:text-white font-medium truncate pr-4">
                {chat.title}
              </span>
              <span className="text-[12.5px] text-[#707070] group-hover:text-[#909090] shrink-0 font-normal">
                {chat.updated_at
                  ? new Date(chat.updated_at).toLocaleDateString()
                  : "Recently"}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
