"use client";

import React, { useState, useEffect } from "react";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Cancel01Icon,
  CheckmarkCircle02Icon,
  PlusSignIcon,
  PencilEdit02Icon,
  Delete02Icon,
  AiBrain01Icon,
  ServerIcon,
  ArrowRight01Icon,
} from "@hugeicons/core-free-icons";
import { useLLMs, useCreateLLM, useUpdateLLM, useDeleteLLM } from "@/lib/hooks";
import { LLMItem } from "@/lib/api";

const PROVIDER_PRESETS: Array<{
  label: string;
  provider: "ollama" | "openai" | "anthropic" | "custom";
  name: string;
  model_name: string;
  url: string;
  port: number | null;
  auth_key_hint: string;
}> = [
  {
    label: "Ollama: Qwen 2.5 (Local)",
    provider: "ollama",
    name: "Qwen 2.5 7B",
    model_name: "qwen2.5:7b",
    url: "http://localhost:11434",
    port: 11434,
    auth_key_hint: "None required for local Ollama",
  },
  {
    label: "Ollama: Llama 3.1 (Local)",
    provider: "ollama",
    name: "Llama 3.1 8B",
    model_name: "llama3.1:8b",
    url: "http://localhost:11434",
    port: 11434,
    auth_key_hint: "None required for local Ollama",
  },
  {
    label: "OpenAI: GPT-4o",
    provider: "openai",
    name: "OpenAI GPT-4o",
    model_name: "gpt-4o",
    url: "https://api.openai.com/v1",
    port: null,
    auth_key_hint: "sk-...",
  },
  {
    label: "Anthropic: Claude 3.5 Sonnet",
    provider: "anthropic",
    name: "Claude 3.5 Sonnet",
    model_name: "claude-3-5-sonnet-20241022",
    url: "https://api.anthropic.com/v1",
    port: null,
    auth_key_hint: "sk-ant-...",
  },
];

export default function LLMSettingsView() {
  const { data: llms = [], isLoading } = useLLMs();
  const createLLMMutation = useCreateLLM();
  const updateLLMMutation = useUpdateLLM();
  const deleteLLMMutation = useDeleteLLM();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingLLM, setEditingLLM] = useState<LLMItem | null>(null);

  // Form State
  const [formName, setFormName] = useState("");
  const [formProvider, setFormProvider] = useState<string>("ollama");
  const [formModelName, setFormModelName] = useState("");
  const [formUrl, setFormUrl] = useState("http://localhost:11434");
  const [formPort, setFormPort] = useState<string>("11434");
  const [formAuthKey, setFormAuthKey] = useState("");
  const [formIsDefault, setFormIsDefault] = useState(false);
  const [formError, setFormError] = useState("");

  const handleOpenAdd = () => {
    setEditingLLM(null);
    setFormName("Qwen 2.5 (Local)");
    setFormProvider("ollama");
    setFormModelName("qwen2.5:7b");
    setFormUrl("http://localhost:11434");
    setFormPort("11434");
    setFormAuthKey("");
    setFormIsDefault(llms.length === 0);
    setFormError("");
    setIsModalOpen(true);
  };

  const handleOpenEdit = (item: LLMItem) => {
    setEditingLLM(item);
    setFormName(item.name);
    setFormProvider(item.provider);
    setFormModelName(item.model_name);
    setFormUrl(item.url);
    setFormPort(item.port ? String(item.port) : "");
    setFormAuthKey(item.auth_key || "");
    setFormIsDefault(!!item.is_default);
    setFormError("");
    setIsModalOpen(true);
  };

  const applyPreset = (preset: (typeof PROVIDER_PRESETS)[number]) => {
    setFormProvider(preset.provider);
    setFormName(preset.name);
    setFormModelName(preset.model_name);
    setFormUrl(preset.url);
    setFormPort(preset.port ? String(preset.port) : "");
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formName.trim()) {
      setFormError("Name is required");
      return;
    }
    if (!formModelName.trim()) {
      setFormError("Model name is required");
      return;
    }
    if (!formUrl.trim()) {
      setFormError("Endpoint URL is required");
      return;
    }

    const payload = {
      name: formName.trim(),
      provider: formProvider,
      model_name: formModelName.trim(),
      url: formUrl.trim(),
      port: formPort.trim() ? parseInt(formPort.trim(), 10) : null,
      auth_key: formAuthKey.trim() || null,
      is_default: formIsDefault,
      temperature: 0.7,
      max_tokens: 4096,
      extra_headers: {},
    };

    try {
      if (editingLLM) {
        await updateLLMMutation.mutateAsync({
          id: editingLLM.id,
          data: payload,
        });
      } else {
        await createLLMMutation.mutateAsync(payload);
      }
      setIsModalOpen(false);
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || err?.message || "Failed to save LLM configuration");
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (confirm(`Are you sure you want to delete "${name}"?`)) {
      try {
        await deleteLLMMutation.mutateAsync(id);
      } catch (err) {
        console.error("Failed to delete LLM", err);
      }
    }
  };

  const handleSetDefault = async (item: LLMItem) => {
    try {
      await updateLLMMutation.mutateAsync({
        id: item.id,
        data: { is_default: true },
      });
    } catch (err) {
      console.error("Failed to set default LLM", err);
    }
  };

  return (
    <div className="space-y-6 font-mono text-[#ededed]">
      {/* Top Header */}
      <div className="flex items-start justify-between pb-2 border-b border-[#282828]">
        <div>
          <h3 className="text-[17px] font-semibold text-[#f0f0f0] tracking-tight">
            LLM Configurations
          </h3>
          <p className="text-[12px] text-[#888888] mt-1 leading-relaxed">
            Configure local models (Ollama, Qwen, Llama) or online provider connections (OpenAI, Anthropic, Custom vLLM endpoints).
          </p>
        </div>

        <button
          type="button"
          onClick={handleOpenAdd}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#2a2a2a] hover:bg-[#343434] text-white text-[12.5px] font-medium border border-[#3b3b3b] hover:border-[#4c4c4c] transition-all cursor-pointer shadow-sm"
        >
          <HugeiconsIcon icon={PlusSignIcon} size={14} strokeWidth={2.5} />
          <span>Add LLM</span>
        </button>
      </div>

      {/* LLMs List */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="py-12 text-center text-[13px] text-[#707070]">
            Loading LLM configurations...
          </div>
        ) : llms.length === 0 ? (
          <div className="p-8 rounded-2xl bg-[#161616] border border-[#262626] text-center flex flex-col items-center justify-center space-y-3">
            <div className="w-10 h-10 rounded-xl bg-[#222222] border border-[#303030] flex items-center justify-center text-[#888888]">
              <HugeiconsIcon icon={AiBrain01Icon} size={20} strokeWidth={1.8} />
            </div>
            <div>
              <p className="text-[14px] font-medium text-[#e0e0e0]">No LLMs configured yet</p>
              <p className="text-[12px] text-[#7a7a7a] mt-0.5">
                Add a local Ollama model or connect an online API to power Tessa.
              </p>
            </div>
            <button
              type="button"
              onClick={handleOpenAdd}
              className="mt-2 flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-white text-black text-[12.5px] font-semibold hover:bg-[#e0e0e0] transition-colors cursor-pointer"
            >
              <HugeiconsIcon icon={PlusSignIcon} size={14} strokeWidth={2.5} />
              <span>Add Your First LLM</span>
            </button>
          </div>
        ) : (
          <div className="space-y-2.5">
            {llms.map((item) => (
              <div
                key={item.id}
                className="p-3.5 rounded-xl bg-[#202020] border border-[#2b2b2b] hover:border-[#383838] transition-all flex items-center justify-between group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-lg bg-[#272727] border border-[#333333] flex items-center justify-center text-[#aaaaaa] shrink-0">
                    {item.provider === "ollama" ? (
                      <HugeiconsIcon icon={ServerIcon} size={16} strokeWidth={2} />
                    ) : (
                      <HugeiconsIcon icon={AiBrain01Icon} size={16} strokeWidth={2} />
                    )}
                  </div>

                  <div className="flex flex-col min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-[13.5px] font-medium text-[#f0f0f0] truncate">
                        {item.name}
                      </span>
                      {item.is_default && (
                        <span className="px-2 py-0.5 rounded-full bg-[#1b3320] text-[#4ade80] border border-[#25522e] text-[10.5px] font-medium tracking-tight">
                          Default
                        </span>
                      )}
                      <span className="px-1.5 py-0.5 rounded-md bg-[#292929] text-[#9a9a9a] border border-[#363636] text-[10.5px] uppercase font-mono">
                        {item.provider}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-[11.5px] text-[#777777] mt-1 font-mono truncate">
                      <span className="text-[#a0a0a0]">{item.model_name}</span>
                      <span>•</span>
                      <span className="truncate">{item.url}{item.port ? `:${item.port}` : ""}</span>
                      {item.auth_key && (
                        <>
                          <span>•</span>
                          <span className="text-[#666666]">API Key set</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0 ml-3">
                  {!item.is_default && (
                    <button
                      type="button"
                      onClick={() => handleSetDefault(item)}
                      className="px-2 py-1 rounded-lg text-[11.5px] text-[#888888] hover:text-[#e0e0e0] hover:bg-[#282828] transition-colors cursor-pointer"
                    >
                      Set Default
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={() => handleOpenEdit(item)}
                    className="p-1.5 text-[#888888] hover:text-white rounded-lg hover:bg-[#2a2a2a] transition-colors cursor-pointer"
                    title="Edit LLM"
                  >
                    <HugeiconsIcon icon={PencilEdit02Icon} size={15} strokeWidth={2} />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(item.id, item.name)}
                    className="p-1.5 text-[#888888] hover:text-[#ef4444] rounded-lg hover:bg-[#2a2a2a] transition-colors cursor-pointer"
                    title="Delete LLM"
                  >
                    <HugeiconsIcon icon={Delete02Icon} size={15} strokeWidth={2} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add / Edit LLM Modal */}
      {isModalOpen && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-[2px] animate-in fade-in duration-150 select-none font-mono"
          onClick={(e) => {
            if (e.target === e.currentTarget) setIsModalOpen(false);
          }}
        >
          <div className="relative w-full max-w-[580px] bg-[#1d1d1d] text-[#ececec] rounded-2xl p-6 shadow-[0_24px_60px_rgba(0,0,0,0.9)] border border-[#333333] flex flex-col space-y-5 animate-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-3 border-b border-[#2b2b2b]">
              <div>
                <h4 className="text-[16px] font-semibold text-white tracking-tight">
                  {editingLLM ? "Edit LLM Configuration" : "Add New LLM"}
                </h4>
                <p className="text-[11.5px] text-[#808080] mt-0.5">
                  Configure connection to local or cloud LLM runtime
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="p-1 text-[#888888] hover:text-white rounded-lg hover:bg-[#282828] transition-colors cursor-pointer"
              >
                <HugeiconsIcon icon={Cancel01Icon} size={16} strokeWidth={2} />
              </button>
            </div>

            {/* Quick Presets (Only when adding) */}
            {!editingLLM && (
              <div className="space-y-1.5">
                <span className="text-[11.5px] text-[#888888] font-medium">
                  Quick Presets
                </span>
                <div className="grid grid-cols-2 gap-2">
                  {PROVIDER_PRESETS.map((p) => (
                    <button
                      key={p.label}
                      type="button"
                      onClick={() => applyPreset(p)}
                      className="px-2.5 py-1.5 rounded-lg bg-[#242424] hover:bg-[#2c2c2c] border border-[#303030] text-left text-[11.5px] text-[#d4d4d4] hover:text-white transition-colors cursor-pointer truncate"
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSave} className="space-y-4">
              {formError && (
                <div className="p-2.5 rounded-lg bg-[#3a1a1a] border border-[#5a2424] text-[#f87171] text-[12px]">
                  {formError}
                </div>
              )}

              {/* Provider & Name Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-[12px] font-medium text-[#c0c0c0]">
                    Provider
                  </label>
                  <select
                    value={formProvider}
                    onChange={(e) => {
                      const val = e.target.value;
                      setFormProvider(val);
                      if (val === "ollama") {
                        setFormUrl("http://localhost:11434");
                        setFormPort("11434");
                      } else if (val === "openai") {
                        setFormUrl("https://api.openai.com/v1");
                        setFormPort("");
                      } else if (val === "anthropic") {
                        setFormUrl("https://api.anthropic.com/v1");
                        setFormPort("");
                      }
                    }}
                    className="w-full bg-[#161616] border border-[#333333] focus:border-[#555555] rounded-lg px-3 py-2 text-[13px] text-white outline-none"
                  >
                    <option value="ollama">Ollama (Local)</option>
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="custom">Custom / vLLM / LMStudio</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[12px] font-medium text-[#c0c0c0]">
                    Display Name
                  </label>
                  <input
                    type="text"
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    placeholder="e.g. Qwen 2.5 7B"
                    className="w-full bg-[#161616] border border-[#333333] focus:border-[#555555] rounded-lg px-3 py-2 text-[13px] text-white placeholder-[#606060] outline-none"
                  />
                </div>
              </div>

              {/* Model Name */}
              <div className="space-y-1">
                <label className="text-[12px] font-medium text-[#c0c0c0]">
                  Model Name (as registered in Ollama / API)
                </label>
                <input
                  type="text"
                  value={formModelName}
                  onChange={(e) => setFormModelName(e.target.value)}
                  placeholder="e.g. qwen2.5:7b, llama3.1:8b, gpt-4o, claude-3-5-sonnet-20241022"
                  className="w-full bg-[#161616] border border-[#333333] focus:border-[#555555] rounded-lg px-3 py-2 text-[13px] text-white placeholder-[#606060] outline-none"
                />
              </div>

              {/* URL & Port */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="sm:col-span-2 space-y-1">
                  <label className="text-[12px] font-medium text-[#c0c0c0]">
                    Endpoint URL
                  </label>
                  <input
                    type="text"
                    value={formUrl}
                    onChange={(e) => setFormUrl(e.target.value)}
                    placeholder="http://localhost:11434"
                    className="w-full bg-[#161616] border border-[#333333] focus:border-[#555555] rounded-lg px-3 py-2 text-[13px] text-white placeholder-[#606060] outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[12px] font-medium text-[#c0c0c0]">
                    Port (Optional)
                  </label>
                  <input
                    type="number"
                    value={formPort}
                    onChange={(e) => setFormPort(e.target.value)}
                    placeholder="11434"
                    className="w-full bg-[#161616] border border-[#333333] focus:border-[#555555] rounded-lg px-3 py-2 text-[13px] text-white placeholder-[#606060] outline-none"
                  />
                </div>
              </div>

              {/* Auth Key (Optional) */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <label className="text-[12px] font-medium text-[#c0c0c0]">
                    Auth Key / API Key (Optional)
                  </label>
                  <span className="text-[11px] text-[#707070]">
                    Leave blank for local Ollama
                  </span>
                </div>
                <input
                  type="password"
                  value={formAuthKey}
                  onChange={(e) => setFormAuthKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full bg-[#161616] border border-[#333333] focus:border-[#555555] rounded-lg px-3 py-2 text-[13px] text-white placeholder-[#606060] outline-none"
                />
              </div>

              {/* Default toggle */}
              <div className="flex items-center justify-between pt-1">
                <div>
                  <span className="text-[13px] text-[#e0e0e0] font-medium">Set as Default Model</span>
                  <p className="text-[11px] text-[#707070]">
                    Used as the default model for new chats and project prompts
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setFormIsDefault(!formIsDefault)}
                  className={`w-11 h-6 rounded-full transition-colors relative cursor-pointer ${
                    formIsDefault ? "bg-[#30643b]" : "bg-[#333333]"
                  }`}
                >
                  <div
                    className={`w-4 h-4 rounded-full bg-white transition-transform absolute top-1 ${
                      formIsDefault ? "right-1" : "left-1"
                    }`}
                  />
                </button>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-[#2b2b2b]">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-[12.5px] text-[#a0a0a0] hover:text-white hover:bg-[#282828] transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createLLMMutation.isPending || updateLLMMutation.isPending}
                  className="px-4 py-2 rounded-xl bg-white hover:bg-[#eaeaea] text-black text-[12.5px] font-semibold transition-colors cursor-pointer disabled:opacity-50"
                >
                  {editingLLM ? "Save Changes" : "Create Configuration"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
