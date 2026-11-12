"use client";

import React, { useState, useEffect, useRef } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import { Cancel01Icon } from "@hugeicons/core-free-icons";

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate?: (project: { name: string; description: string }) => void;
}

export default function CreateProjectModal({
  isOpen,
  onClose,
  onCreate,
}: CreateProjectModalProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const nameInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setName("");
      setDescription("");
      setTimeout(() => {
        nameInputRef.current?.focus();
      }, 50);
    }
  }, [isOpen]);

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
    if (!name.trim()) return;
    onCreate?.({ name: name.trim(), description: description.trim() });
    onClose();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Create a project"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-[2px] animate-in fade-in duration-150 select-none font-mono"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="relative w-full max-w-[460px] bg-[#272727] text-[#ebebeb] rounded-2xl p-5 shadow-[0_20px_50px_rgba(0,0,0,0.8)] border border-[#383838] animate-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between pb-4">
          <h2 className="text-[15px] font-semibold text-[#f2f2f2] tracking-tight">
            Create a project
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
          {/* Question 1: What are you working on? */}
          <div className="space-y-1.5">
            <label className="block text-[12.5px] font-medium text-[#cccccc]">
              What are you working on?
            </label>
            <input
              ref={nameInputRef}
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Name your project"
              required
              className="w-full h-10 px-3 bg-[#1e1e1e] border border-[#343434] focus:border-[#3b82f6] rounded-xl text-[13px] text-[#f2f2f2] placeholder-[#6b6b6b] outline-none transition-colors"
            />
          </div>

          {/* Question 2: What are you trying to achieve? */}
          <div className="space-y-1.5">
            <label className="block text-[12.5px] font-medium text-[#cccccc]">
              What are you trying to achieve?
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe your project, goals, subject, etc..."
              rows={3}
              className="w-full p-3 bg-[#1e1e1e] border border-[#343434] focus:border-[#3b82f6] rounded-xl text-[13px] text-[#f2f2f2] placeholder-[#6b6b6b] outline-none resize-none transition-colors"
            />
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-2.5 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-[#383838] hover:bg-[#424242] text-[13px] font-medium text-[#e2e2e2] transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!name.trim()}
              className="px-4 py-2 rounded-xl bg-white hover:bg-[#eaeaea] disabled:opacity-50 disabled:cursor-not-allowed text-[13px] font-semibold text-black transition-all cursor-pointer shadow-sm"
            >
              Create project
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
