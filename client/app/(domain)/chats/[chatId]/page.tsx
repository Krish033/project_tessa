"use client";

import React, { useState, Suspense, useRef } from "react";
import { useParams } from "next/navigation";
import { HugeiconsIcon } from "@hugeicons/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import AttachMenu from "@/components/shared/AttachMenu";
import MicMenu from "@/components/shared/MicMenu";
import {
  Add01Icon,
  Mic01Icon,
  AudioWaveformIcon,
  ReloadIcon,
  PencilEdit02Icon,
  Copy01Icon,
  VolumeHighIcon,
  ThumbsUpIcon,
  ThumbsDownIcon,
  ArrowDown01Icon,
  ArrowUp02Icon,
} from "@hugeicons/core-free-icons";

function ChatDetailContent() {
  const params = useParams();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [inputMessage, setInputMessage] = useState("");
  const [isAttachOpen, setIsAttachOpen] = useState(false);
  const [isMicOpen, setIsMicOpen] = useState(false);
  const [copiedUser, setCopiedUser] = useState(false);
  const [copiedAi, setCopiedAi] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);

  const handleCopy = (text: string, isAi = false) => {
    navigator.clipboard.writeText(text);
    if (isAi) {
      setCopiedAi(true);
      setTimeout(() => setCopiedAi(false), 2000);
    } else {
      setCopiedUser(true);
      setTimeout(() => setCopiedUser(false), 2000);
    }
  };

  const userPromptText = `Give me a description for a testing event conducted only for testing, no public arrival expected`;

  const aiResponseText = `### Test Event - Internal Use Only

This event was created solely for testing calendar invite functionality (creation, updates, cancellations, and attachments). No attendance is expected and no action is required. Please disregard this invitation.`;

  return (
    <div className="flex-1 flex flex-col min-h-0 h-full bg-[#141414] text-white font-mono overflow-hidden">
      {/* Scrollable Conversation Stream (Middle Section: ONLY this section scrolls) */}
      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-8 flex justify-center relative">
        <div className="w-full max-w-[780px] flex flex-col space-y-7 pb-36">
          {/* USER MESSAGE BUBBLE */}
          <div className="flex flex-col items-end group/user">
            <div className="max-w-[85%] bg-[#212121] border border-[#2b2b2b] rounded-2xl px-5 py-4 text-[#dcdcdc] text-[15px] leading-relaxed shadow-md select-text selection:bg-[#3d3d3d] selection:text-white">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ children }) => <p className="whitespace-pre-wrap">{children}</p>,
                }}
              >
                {userPromptText}
              </ReactMarkdown>
            </div>

            {/* Bubble Action Controls: Shown ONLY on hover */}
            <div className="flex items-center gap-2.5 mt-2 text-[#777777] text-[12px] pr-2 opacity-0 group-hover/user:opacity-100 transition-opacity duration-150 select-none">
              <span className="text-[11.5px] text-[#6e6e6e]">2 hours ago</span>
              <button
                type="button"
                className="hover:text-white transition-colors p-1 rounded hover:bg-[#282828] cursor-pointer"
                title="Retry prompt"
              >
                <HugeiconsIcon icon={ReloadIcon} size={13} strokeWidth={2} />
              </button>
              <button
                type="button"
                className="hover:text-white transition-colors p-1 rounded hover:bg-[#282828] cursor-pointer"
                title="Edit prompt"
              >
                <HugeiconsIcon icon={PencilEdit02Icon} size={13} strokeWidth={2} />
              </button>
              <button
                type="button"
                onClick={() => handleCopy(userPromptText, false)}
                className="hover:text-white transition-colors p-1 rounded hover:bg-[#282828] cursor-pointer"
                title="Copy prompt"
              >
                <HugeiconsIcon icon={Copy01Icon} size={13} strokeWidth={2} />
              </button>
            </div>
          </div>

          {/* AI RESPONSE MESSAGE */}
          <div className="flex flex-col items-start w-full leading-relaxed space-y-3 pt-1 group/ai">
            {/* Markdown rendered body with full text selection support */}
            <div className="w-full text-[#d4d4d4] select-text selection:bg-[#3d3d3d] selection:text-white space-y-2.5">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => (
                    <h1 className="text-[19px] font-semibold text-white tracking-tight mb-2">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-[17px] font-semibold text-white tracking-tight mb-2">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-[16px] font-semibold text-white tracking-tight mb-1.5">
                      {children}
                    </h3>
                  ),
                  p: ({ children }) => (
                    <p className="leading-relaxed text-[#d4d4d4] text-[15px] max-w-3xl mb-2">
                      {children}
                    </p>
                  ),
                  ul: ({ children }) => (
                    <ul className="space-y-1.5 pl-4 list-disc text-[#bfbfbf] text-[15px] my-2">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="space-y-1.5 pl-4 list-decimal text-[#bfbfbf] text-[15px] my-2">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => <li className="pl-1 text-[15px]">{children}</li>,
                  code: ({ className, children }) => {
                    const isInline = !className;
                    return isInline ? (
                      <code className="px-1.5 py-0.5 rounded bg-[#242424] text-[#ececec] text-[13.5px] font-mono border border-[#333333]">
                        {children}
                      </code>
                    ) : (
                      <pre className="p-3.5 rounded-xl bg-[#1c1c1c] border border-[#2b2b2b] overflow-x-auto text-[13.5px] my-2.5">
                        <code>{children}</code>
                      </pre>
                    );
                  },
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-2 border-[#444444] pl-3 text-[#999999] italic text-[15px] my-2">
                      {children}
                    </blockquote>
                  ),
                }}
              >
                {aiResponseText}
              </ReactMarkdown>
            </div>

            {/* AI Response Action Icons Row: Copy, Read aloud, Upvote, Downvote, Retry */}
            <div className="flex items-center gap-1.5 pt-1 text-[#888888] select-none">
              {/* Copy */}
              <button
                type="button"
                onClick={() => handleCopy(aiResponseText, true)}
                className="p-1.5 rounded-lg hover:text-white hover:bg-[#262626] transition-colors cursor-pointer"
                title="Copy response"
              >
                <HugeiconsIcon icon={Copy01Icon} size={14} strokeWidth={1.8} />
              </button>

              {/* Read Aloud / Speaker */}
              <button
                type="button"
                className="p-1.5 rounded-lg hover:text-white hover:bg-[#262626] transition-colors cursor-pointer"
                title="Read aloud"
              >
                <HugeiconsIcon icon={VolumeHighIcon} size={14} strokeWidth={1.8} />
              </button>

              {/* Thumbs Up */}
              <button
                type="button"
                onClick={() => setLiked(liked === true ? null : true)}
                className={`p-1.5 rounded-lg hover:text-white hover:bg-[#262626] transition-colors cursor-pointer ${
                  liked === true ? "text-white" : ""
                }`}
                title="Good response"
              >
                <HugeiconsIcon icon={ThumbsUpIcon} size={14} strokeWidth={1.8} />
              </button>

              {/* Thumbs Down */}
              <button
                type="button"
                onClick={() => setLiked(liked === false ? null : false)}
                className={`p-1.5 rounded-lg hover:text-white hover:bg-[#262626] transition-colors cursor-pointer ${
                  liked === false ? "text-white" : ""
                }`}
                title="Bad response"
              >
                <HugeiconsIcon icon={ThumbsDownIcon} size={14} strokeWidth={1.8} />
              </button>

              {/* Retry / Regenerate */}
              <button
                type="button"
                className="p-1.5 rounded-lg hover:text-white hover:bg-[#262626] transition-colors cursor-pointer"
                title="Regenerate response"
              >
                <HugeiconsIcon icon={ReloadIcon} size={14} strokeWidth={1.8} />
              </button>

              {copiedAi && (
                <span className="text-[11px] text-green-400 font-mono ml-1">
                  Copied
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* BOTTOM INPUT DOCK & DISCLAIMER (Separate non-overlapping fixed footer) */}
      <div className="shrink-0 w-full bg-[#141414] border-t border-[#222222] pt-3 pb-3 px-4 flex flex-col items-center select-none">
        {/* Hidden file input for file uploading */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              setInputMessage((prev) =>
                prev ? `${prev} [Attached ${e.target.files?.length} files]` : `[Attached ${e.target.files?.length} files]`
              );
            }
          }}
        />

        <div className="w-full max-w-[780px] flex flex-col items-center relative">
          {/* Main Message Pill Input Box */}
          <div className="w-full bg-[#202020] border border-[#2d2d2d] focus-within:border-[#444444] rounded-2xl px-3.5 py-2.5 flex items-center gap-3 shadow-lg transition-all relative">
            {/* Left '+' Add button with Attach Menu */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setIsAttachOpen(!isAttachOpen)}
                className={`text-[#888888] hover:text-white transition-colors shrink-0 p-0.5 rounded-lg cursor-pointer ${
                  isAttachOpen ? "text-white bg-[#303030]" : ""
                }`}
                title="Add attachment or skill"
              >
                <HugeiconsIcon icon={Add01Icon} size={16} strokeWidth={2.4} />
              </button>

              <AttachMenu
                isOpen={isAttachOpen}
                onClose={() => setIsAttachOpen(false)}
                onUploadFiles={() => fileInputRef.current?.click()}
              />
            </div>

            {/* Message input */}
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey && inputMessage.trim()) {
                  e.preventDefault();
                  setInputMessage("");
                }
              }}
              placeholder="Write a message..."
              className="flex-1 bg-transparent border-none outline-none text-[15px] text-[#f0f0f0] placeholder-[#666666] font-mono select-text leading-normal"
            />

            {/* Right controls: Mic and Audio/Send button */}
            <div className="flex items-center gap-1 text-[#888888] shrink-0">
              {/* Mic and chevron split button container */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setIsMicOpen(!isMicOpen)}
                  className={`flex items-center gap-0.5 p-1 rounded-lg transition-colors cursor-pointer hover:text-white ${
                    isMicOpen ? "text-white bg-[#303030]" : "hover:bg-[#282828]"
                  }`}
                  title="Voice input & dictation settings"
                >
                  <HugeiconsIcon icon={Mic01Icon} size={15} strokeWidth={2} />
                  <HugeiconsIcon
                    icon={ArrowDown01Icon}
                    size={11}
                    strokeWidth={2.5}
                    className={`text-[#777777] transition-transform duration-150 ${
                      isMicOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>

                <MicMenu
                  isOpen={isMicOpen}
                  onClose={() => setIsMicOpen(false)}
                />
              </div>

              {inputMessage.trim().length > 0 ? (
                <button
                  type="button"
                  onClick={() => setInputMessage("")}
                  className="w-6 h-6 rounded-md bg-white text-black hover:bg-[#eaeaea] flex items-center justify-center transition-all cursor-pointer shadow-md active:scale-95"
                  title="Send message"
                >
                  <HugeiconsIcon
                    icon={ArrowUp02Icon}
                    size={14}
                    strokeWidth={2.4}
                    className="text-black"
                  />
                </button>
              ) : (
                <button
                  type="button"
                  className="hover:text-white transition-colors p-1 cursor-pointer"
                  title="Audio speech"
                >
                  <HugeiconsIcon icon={AudioWaveformIcon} size={16} strokeWidth={2} />
                </button>
              )}
            </div>
          </div>

          {/* Footer Disclaimer & Model Tag */}
          <div className="w-full flex items-center justify-between text-[11px] text-[#666666] px-2 pt-2 select-none">
            <span>Claude is AI and can make mistakes. Please double-check responses.</span>
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
