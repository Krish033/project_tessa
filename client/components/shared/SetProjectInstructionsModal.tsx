"use client";

import React, { useState, useEffect, useRef } from "react";

interface SetProjectInstructionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectName?: string;
  initialInstructions?: string;
  onSave?: (instructions: string) => void;
}

export default function SetProjectInstructionsModal({
  isOpen,
  onClose,
  projectName = "Broward Partnership for kids",
  initialInstructions = "",
  onSave,
}: SetProjectInstructionsModalProps) {
  const [instructions, setInstructions] = useState(initialInstructions);
  const [hasAttemptedSubmit, setHasAttemptedSubmit] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isOpen) {
      setInstructions(initialInstructions);
      setHasAttemptedSubmit(false);
      setTimeout(() => {
        textareaRef.current?.focus();
      }, 50);
    }
  }, [isOpen, initialInstructions]);

  // Close on Escape
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
    if (!instructions.trim()) {
      setHasAttemptedSubmit(true);
      textareaRef.current?.focus();
      return;
    }
    onSave?.(instructions.trim());
    onClose();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Set project instructions"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/65 backdrop-blur-[2px] animate-in fade-in duration-150 select-none font-mono"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-[550px] bg-[#272727] text-[#ebebeb] rounded-2xl p-6 shadow-[0_24px_60px_rgba(0,0,0,0.85)] border border-[#383838] animate-in zoom-in-95 duration-150">
        {/* Title */}
        <h2 className="text-[15px] font-semibold text-[#f2f2f2] tracking-tight mb-2.5">
          Set project instructions
        </h2>

        {/* Description */}
        <p className="text-[12px] text-[#9a9a9a] leading-relaxed mb-4">
          Provide Claude with relevant instructions and information for chats within{" "}
          <span className="text-[#cccccc]">{projectName}</span>. This will work alongside your{" "}
          <button
            type="button"
            className="text-[#3b82f6] hover:underline cursor-pointer"
          >
            profile instructions
          </button>{" "}
          and the selected style in a chat.
        </p>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <textarea
              ref={textareaRef}
              value={instructions}
              onChange={(e) => {
                setInstructions(e.target.value);
                if (e.target.value.trim()) setHasAttemptedSubmit(false);
              }}
              placeholder="Think step by step and show reasoning for complex problems. Use specific examples."
              rows={9}
              className="w-full p-3.5 bg-[#2c2c2c] border border-[#2563eb] rounded-xl text-[13px] text-[#f2f2f2] placeholder-[#666666] outline-none resize-none transition-colors leading-relaxed"
            />

            {/* Validation tooltip matching screenshot if empty on submit */}
            {hasAttemptedSubmit && !instructions.trim() && (
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#1e1e1e] border border-[#3b3b3b] text-[#e0e0e0] text-[11px] px-2.5 py-1 rounded-md shadow-xl pointer-events-none animate-in fade-in zoom-in-95">
                Please fill out this field.
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex items-center justify-end gap-2.5 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-[#363636] hover:bg-[#404040] text-[12.5px] font-medium text-[#e0e0e0] transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-[#363636] hover:bg-[#404040] text-[12.5px] font-medium text-[#e0e0e0] transition-colors cursor-pointer"
            >
              Save instructions
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
