"use client";

import React, { useState, useEffect, useRef } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import { Cancel01Icon } from "@hugeicons/core-free-icons";

interface AddTextContentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd?: (data: { title: string; content: string }) => void;
}

export default function AddTextContentModal({
  isOpen,
  onClose,
  onAdd,
}: AddTextContentModalProps) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const titleInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTitle("");
      setContent("");
      setTimeout(() => {
        titleInputRef.current?.focus();
      }, 50);
    }
  }, [isOpen]);

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() && !content.trim()) return;
    onAdd?.({ title: title.trim(), content: content.trim() });
    onClose();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Add text content"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/65 backdrop-blur-[2px] animate-in fade-in duration-150 select-none font-mono"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-[550px] bg-[#272727] text-[#ebebeb] rounded-2xl p-6 shadow-[0_24px_60px_rgba(0,0,0,0.85)] border border-[#383838] animate-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between pb-3">
          <h2 className="text-[15px] font-semibold text-[#f2f2f2] tracking-tight">
            Add text content
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-[#8c8c8c] hover:text-white rounded-lg hover:bg-[#343434] transition-colors cursor-pointer"
            aria-label="Close"
          >
            <HugeiconsIcon icon={Cancel01Icon} size={16} strokeWidth={2} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div className="space-y-1.5">
            <label className="block text-[12.5px] font-medium text-[#cccccc]">
              Title
            </label>
            <input
              ref={titleInputRef}
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Name your content"
              className="w-full h-10 px-3.5 bg-[#2c2c2c] border border-[#2563eb] rounded-xl text-[13px] text-[#f2f2f2] placeholder-[#666666] outline-none transition-colors"
            />
          </div>

          {/* Content */}
          <div className="space-y-1.5">
            <label className="block text-[12.5px] font-medium text-[#cccccc]">
              Content
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Type or paste in content..."
              rows={8}
              className="w-full p-3.5 bg-[#222222] border border-[#333333] focus:border-[#444444] rounded-xl text-[13px] text-[#f2f2f2] placeholder-[#555555] outline-none resize-none transition-colors leading-relaxed"
            />
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-2.5 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-[#363636] hover:bg-[#404040] text-[12.5px] font-medium text-[#e0e0e0] transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-white hover:bg-[#eaeaea] text-[12.5px] font-semibold text-black transition-all cursor-pointer shadow-sm"
            >
              Add Content
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
