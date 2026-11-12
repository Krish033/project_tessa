"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Add01Icon,
  Mic01Icon,
  ArrowDown01Icon,
  AudioWaveformIcon,
  CodeXmlIcon,
  PencilEdit02Icon,
  GraduationCapIcon,
  Coffee02Icon,
  Idea01Icon,
  ArrowUp02Icon,
} from "@hugeicons/core-free-icons";

export default function HomePage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [activeMode, setActiveMode] = useState<"Chat" | "Cowork">("Chat");

  const chips = [
    { label: "Code", icon: CodeXmlIcon },
    { label: "Write", icon: PencilEdit02Icon },
    { label: "Learn", icon: GraduationCapIcon },
    { label: "Life stuff", icon: Coffee02Icon },
    { label: "Tessa's choice", icon: Idea01Icon },
  ];

  const handleSend = () => {
    if (!prompt.trim()) return;
    // Generate a random alphanumeric chat ID (e.g. chat-7f2a9b)
    const randomChatId = "chat-" + Math.random().toString(36).substring(2, 9);
    router.push(`/chats/${randomChatId}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isTyping = prompt.trim().length > 0;

  return (
    <div className="relative min-h-full flex flex-col items-center justify-center px-4 bg-[#141414] text-white font-mono select-none">
      {/* Main Container */}
      <div className="w-full max-w-[680px] flex flex-col items-center -mt-8">
        {/* Main Heading */}
        <div className="flex items-center gap-3.5 mb-7">
          <h1 className="text-3xl md:text-4xl font-normal text-[#f3f3f3] tracking-tight">
            How can i help you today?
          </h1>
        </div>

        {/* Input Box Card */}
        <div className="w-full bg-[#1e1e1e] border border-[#2d2d2d] hover:border-[#383838] focus-within:border-[#444444] rounded-2xl p-3.5 transition-all shadow-xl">
          {/* Text Area / Input */}
          <div className="min-h-[58px] px-1 pt-0.5">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type / for skills"
              rows={2}
              className="w-full bg-transparent resize-none border-none outline-none text-[#ececec] placeholder-[#666666] text-[14px] leading-relaxed font-mono"
            />
          </div>

          {/* Bottom Bar Controls inside the Box */}
          <div className="flex items-center justify-between pt-2 mt-1 border-t border-transparent">
            {/* Left Controls: Add button + Mode Switcher */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="w-7 h-7 rounded-lg bg-transparent hover:bg-[#282828] text-[#8e8e8e] hover:text-white flex items-center justify-center transition-colors cursor-pointer"
                title="Add attachment or skill"
              >
                <HugeiconsIcon icon={Add01Icon} size={17} strokeWidth={2.2} />
              </button>

              {/* Chat / Cowork pill toggle */}
              <div className="flex items-center bg-[#151515] p-0.5 rounded-lg border border-[#2b2b2b] text-[12px]">
                <button
                  type="button"
                  onClick={() => setActiveMode("Chat")}
                  className={`px-2.5 py-0.5 rounded-md transition-colors cursor-pointer ${
                    activeMode === "Chat"
                      ? "bg-[#2c2c2c] text-white font-medium shadow-sm"
                      : "text-[#7f7f7f] hover:text-white"
                  }`}
                >
                  Chat
                </button>
                <button
                  type="button"
                  onClick={() => setActiveMode("Cowork")}
                  className={`px-2.5 py-0.5 rounded-md transition-colors cursor-pointer ${
                    activeMode === "Cowork"
                      ? "bg-[#2c2c2c] text-white font-medium shadow-sm"
                      : "text-[#7f7f7f] hover:text-white"
                  }`}
                >
                  Cowork
                </button>
              </div>
            </div>

            {/* Right Controls: Model selector + Mic + Audio/Send button */}
            <div className="flex items-center gap-2.5 text-[#888888]">
              {/* Model Picker */}
              <button
                type="button"
                className="flex items-center gap-1.5 px-2 py-1 rounded-lg hover:bg-[#282828] hover:text-white transition-colors text-[12px] cursor-pointer"
              >
                <span className="font-medium text-[#cccccc]">Sonnet 3.5</span>
                <span className="text-[#777777] text-[11px]">Medium</span>
              </button>

              {/* Mic Icon with small menu indicator */}
              <button
                type="button"
                className="flex items-center gap-0.5 p-1 rounded-lg hover:bg-[#282828] text-[#8e8e8e] hover:text-white transition-colors cursor-pointer"
                title="Voice input"
              >
                <HugeiconsIcon icon={Mic01Icon} size={15} strokeWidth={2} />
                <HugeiconsIcon icon={ArrowDown01Icon} size={11} strokeWidth={2.5} className="text-[#666666]" />
              </button>

              {/* Audio Waveform icon when empty, or Send button when typing */}
              {isTyping ? (
                <button
                  type="button"
                  onClick={handleSend}
                  title="Send message"
                  className="w-7 h-7 rounded-lg bg-white text-black hover:bg-[#eaeaea] flex items-center justify-center transition-all cursor-pointer shadow-md active:scale-95"
                >
                  <HugeiconsIcon
                    icon={ArrowUp02Icon}
                    size={16}
                    strokeWidth={2.4}
                    className="text-black"
                  />
                </button>
              ) : (
                <button
                  type="button"
                  className="p-1 rounded-lg hover:bg-[#282828] text-[#8e8e8e] hover:text-white transition-colors cursor-pointer"
                  title="Start live voice"
                >
                  <HugeiconsIcon icon={AudioWaveformIcon} size={16} strokeWidth={2} />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Suggestion / Action Chips */}
        <div className="flex flex-wrap items-center justify-center gap-2 mt-5">
          {chips.map((chip) => (
            <button
              key={chip.label}
              type="button"
              onClick={() => setPrompt(`/${chip.label.toLowerCase()}`)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#1e1e1e] hover:bg-[#272727] border border-[#2b2b2b] hover:border-[#383838] text-[12px] text-[#cccccc] hover:text-white transition-all shadow-sm cursor-pointer"
            >
              <HugeiconsIcon
                icon={chip.icon}
                size={14}
                strokeWidth={2}
                className="text-[#999999]"
              />
              <span>{chip.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
