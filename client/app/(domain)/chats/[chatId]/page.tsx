"use client";

import React, { useState, Suspense } from "react";
import { useParams } from "next/navigation";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Add01Icon,
  Mic01Icon,
  ArrowDown01Icon,
  AudioWaveformIcon,
  ReloadIcon,
  PencilEdit02Icon,
  Copy01Icon,
  ArrowRight01Icon,
} from "@hugeicons/core-free-icons";

function ChatDetailContent() {
  const params = useParams();
  const [inputMessage, setInputMessage] = useState("");
  const [copied, setCopied] = useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const userPromptText = `Our first case

Investigation: The Black Dahlia Murder
• Victim: Elizabeth Short, 22
• Location: Los Angeles, California, USA
• Year: 1947
• Status: Unsolved
• Difficulty: Expert
• Historical significance: One of America's most infamous unsolved murders

give me the case details,`;

  return (
    <div className="relative h-full flex flex-col bg-[#141414] text-white font-mono select-none overflow-hidden">
      {/* Scrollable Conversation Stream */}
      <div className="flex-1 overflow-y-auto px-4 py-8 flex justify-center">
        <div className="w-full max-w-[760px] flex flex-col space-y-6 pb-28">
          {/* USER MESSAGE BUBBLE (Right aligned card) */}
          <div className="flex flex-col items-end">
            <div className="max-w-[85%] bg-[#212121] border border-[#2b2b2b] rounded-2xl p-5 text-[#dcdcdc] text-[13.5px] leading-relaxed shadow-md">
              <div className="font-semibold text-white mb-2">Our first case</div>
              <div className="mb-3 text-[#d1d1d1]">Investigation: The Black Dahlia Murder</div>
              <ul className="space-y-1 mb-4 text-[#bfbfbf] pl-2">
                <li>• Victim: Elizabeth Short, 22</li>
                <li>• Location: Los Angeles, California, USA</li>
                <li>• Year: 1947</li>
                <li>• Status: Unsolved</li>
                <li>• Difficulty: Expert</li>
                <li>• Historical significance: One of America&apos;s most infamous unsolved murders</li>
              </ul>
              <div className="text-white">give me the case details,</div>
            </div>

            {/* Timestamp & message actions */}
            <div className="flex items-center gap-2.5 mt-2 text-[#737373] text-[12px] pr-1">
              <span>yesterday</span>
              <button
                type="button"
                title="Retry / Regenerate"
                className="hover:text-white transition-colors"
              >
                <HugeiconsIcon icon={ReloadIcon} size={13} strokeWidth={2} />
              </button>
              <button
                type="button"
                title="Edit message"
                className="hover:text-white transition-colors"
              >
                <HugeiconsIcon icon={PencilEdit02Icon} size={13} strokeWidth={2} />
              </button>
              <button
                type="button"
                title="Copy prompt"
                onClick={() => handleCopy(userPromptText)}
                className="hover:text-white transition-colors"
              >
                <HugeiconsIcon icon={Copy01Icon} size={13} strokeWidth={2} />
              </button>
            </div>
          </div>

          {/* ASSISTANT RESPONSE SECTION */}
          <div className="flex flex-col items-start space-y-3 pt-2 text-[#dcdcdc] text-[13.5px] leading-relaxed">
            {/* Thinking / Tool call step collapse */}
            <button
              type="button"
              className="flex items-center gap-1.5 text-[12.5px] text-[#858585] hover:text-[#cccccc] transition-colors py-1"
            >
              <span>Weighing whether a search would update the case status</span>
              <HugeiconsIcon icon={ArrowRight01Icon} size={12} strokeWidth={2.5} />
            </button>

            {/* Answer Content */}
            <div className="space-y-4">
              <h2 className="text-[15px] font-semibold text-white tracking-wide">
                The Black Dahlia Murder: Case File
              </h2>

              <p className="text-[#cccccc]">
                <strong className="text-white font-medium">Victim:</strong> Elizabeth Short, 22, born in Massachusetts in 1924. She moved to California hoping to break into acting and was living between temporary arrangements in LA and the San Diego area.
              </p>

              <p className="text-[#cccccc]">
                <strong className="text-white font-medium">Discovery:</strong> On the morning of January 15, 1947, a woman walking with her young daughter found the body in a vacant lot in the Leimert Park area of Los Angeles.
              </p>

              <div>
                <p className="font-medium text-white mb-2">Condition of the body:</p>
                <ul className="space-y-1 pl-3 text-[#bfbfbf]">
                  <li>• Severed cleanly at the waist</li>
                  <li>• Drained of blood and washed</li>
                  <li>• Posed with arms raised above the head</li>
                  <li>• Mouth slashed from the corners toward ears</li>
                  <li>• Cause of death per autopsy: hemorrhage from facial lacerations and blows to head</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Scroll-to-bottom indicator button */}
      <div className="absolute bottom-[92px] left-1/2 -translate-x-1/2 z-10">
        <button
          type="button"
          className="w-7 h-7 rounded-full bg-[#262626] border border-[#383838] hover:bg-[#333333] text-[#cccccc] hover:text-white flex items-center justify-center shadow-lg transition-all"
          title="Scroll to bottom"
        >
          <HugeiconsIcon icon={ArrowDown01Icon} size={14} strokeWidth={2.5} />
        </button>
      </div>

      {/* BOTTOM INPUT DOCK & DISCLAIMER */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#141414] via-[#141414] to-transparent pt-4 pb-3 px-4 flex flex-col items-center">
        <div className="w-full max-w-[760px] flex flex-col items-center">
          {/* Main Message Pill Input Box */}
          <div className="w-full bg-[#202020] border border-[#2d2d2d] focus-within:border-[#444444] rounded-2xl px-3.5 py-2.5 flex items-center gap-3 shadow-2xl transition-all">
            {/* Left '+' Add button */}
            <button
              type="button"
              className="text-[#888888] hover:text-white transition-colors shrink-0"
              title="Add attachment"
            >
              <HugeiconsIcon icon={Add01Icon} size={16} strokeWidth={2.4} />
            </button>

            {/* Message input */}
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Write a message..."
              className="flex-1 bg-transparent border-none outline-none text-[13.5px] text-[#f0f0f0] placeholder-[#666666] font-mono"
            />

            {/* Right voice & dictation buttons */}
            <div className="flex items-center gap-2 text-[#888888] shrink-0">
              <button
                type="button"
                className="hover:text-white transition-colors p-1"
                title="Voice input"
              >
                <HugeiconsIcon icon={Mic01Icon} size={16} strokeWidth={2} />
              </button>
              <button
                type="button"
                className="hover:text-white transition-colors p-1"
                title="Audio speech"
              >
                <HugeiconsIcon icon={AudioWaveformIcon} size={16} strokeWidth={2} />
              </button>
            </div>
          </div>

          {/* Footer Disclaimer & Model Tag */}
          <div className="w-full flex items-center justify-between text-[11px] text-[#666666] px-2 pt-2 select-none">
            <span>Claude is AI and can make mistakes. Please double-check cited sources.</span>
            <span className="text-[#7d7d7d] font-medium">Sonnet 3.5 Medium</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ChatDetailPage() {
  return (
    <Suspense fallback={<div className="h-full bg-[#141414]" />}>
      <ChatDetailContent />
    </Suspense>
  );
}
