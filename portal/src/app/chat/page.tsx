"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Send, Plus, Trash2, MessageSquare, X, Pencil, Check, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatSession {
  id: string;
  title: string | null;
  model: string;
  created_at: string;
  updated_at: string;
}

interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

const MODELS = [
  { id: "claude-sonnet-4-6", label: "Claude Sonnet", provider: "anthropic" },
  { id: "claude-opus-4-6", label: "Claude Opus", provider: "anthropic" },
  { id: "claude-haiku-4-5", label: "Claude Haiku", provider: "anthropic" },
  { id: "gpt-4o", label: "GPT-4o", provider: "openai" },
  { id: "gpt-4o-mini", label: "GPT-4o mini", provider: "openai" },
] as const;

type ModelId = (typeof MODELS)[number]["id"];

function formatRelative(iso: string): string {
  const now = Date.now();
  const then = new Date(iso).getTime();
  const diff = now - then;
  if (diff < 60000) return "just now";
  if (diff < 3600000) return Math.floor(diff / 60000) + "m ago";
  if (diff < 86400000) return Math.floor(diff / 3600000) + "h ago";
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function ModelBadge({ modelId }: { modelId: string }) {
  const model = MODELS.find((m) => m.id === modelId);
  const isOpenAI = model?.provider === "openai";
  return (
    <span
      className="text-[10px] font-medium px-1.5 py-0.5 rounded"
      style={{
        backgroundColor: isOpenAI ? "#10a37f22" : "#FE500022",
        color: isOpenAI ? "#10a37f" : "#FE5000",
      }}
    >
      {model?.label ?? modelId}
    </span>
  );
}

function ModelPicker({
  value,
  onChange,
}: {
  value: ModelId;
  onChange: (m: ModelId) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const current = MODELS.find((m) => m.id === value) ?? MODELS[0];

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium text-foreground hover:bg-muted transition-colors"
      >
        <ModelBadge modelId={value} />
        <ChevronDown className="h-3 w-3 text-muted-foreground" />
      </button>
      {open && (
        <div className="absolute bottom-full mb-1 left-0 z-50 min-w-[160px] rounded-lg border bg-popover shadow-lg py-1">
          {MODELS.map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => { onChange(m.id); setOpen(false); }}
              className={cn(
                "w-full flex items-center gap-2 px-3 py-1.5 text-xs text-left hover:bg-muted transition-colors",
                value === m.id && "font-semibold"
              )}
            >
              <span
                className="h-1.5 w-1.5 rounded-full shrink-0"
                style={{ backgroundColor: m.provider === "openai" ? "#10a37f" : "#FE5000" }}
              />
              {m.label}
              {value === m.id && <Check className="h-3 w-3 ml-auto" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [model, setModel] = useState<ModelId>("claude-sonnet-4-6");
  const [streaming, setStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [editingMsgId, setEditingMsgId] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);
  useEffect(() => { loadSessions(); }, []);

  async function loadSessions() {
    const res = await fetch("/api/chat/sessions");
    if (res.ok) {
      const data = await res.json() as { sessions: ChatSession[] };
      setSessions(data.sessions);
    }
  }

  async function openSession(session: ChatSession) {
    setActiveSessionId(session.id);
    setModel((session.model as ModelId) ?? "claude-sonnet-4-6");
    const res = await fetch(`/api/chat/sessions/${session.id}`);
    if (res.ok) {
      const data = await res.json() as { messages: ChatMessage[] };
      setMessages(data.messages);
    }
  }

  async function newSession() {
    const res = await fetch("/api/chat/sessions", { method: "POST" });
    if (!res.ok) return null;
    const data = await res.json() as { session: ChatSession };
    setSessions((prev) => [data.session, ...prev]);
    setActiveSessionId(data.session.id);
    setMessages([]);
    return data.session.id;
  }

  async function deleteSession(sessionId: string, e: React.MouseEvent) {
    e.stopPropagation();
    await fetch(`/api/chat/sessions/${sessionId}`, { method: "DELETE" });
    setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    if (activeSessionId === sessionId) {
      setActiveSessionId(null);
      setMessages([]);
    }
  }

  async function handleModelChange(newModel: ModelId) {
    setModel(newModel);
    if (activeSessionId) {
      await fetch(`/api/chat/sessions/${activeSessionId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: newModel }),
      });
      setSessions((prev) => prev.map((s) => s.id === activeSessionId ? { ...s, model: newModel } : s));
    }
  }

  async function sendMessage(content?: string, sessionId?: string) {
    const msgContent = (content ?? input).trim();
    if (!msgContent || streaming) return;

    let sid = sessionId ?? activeSessionId;
    if (!sid) {
      sid = await newSession();
      if (!sid) return;
    }

    if (!content) {
      setInput("");
      if (textareaRef.current) textareaRef.current.style.height = "auto";
    }

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      session_id: sid,
      role: "user",
      content: msgContent,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    const assistantMsgId = crypto.randomUUID();
    setMessages((prev) => [...prev, {
      id: assistantMsgId,
      session_id: sid,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    }]);
    setStreaming(true);

    abortRef.current = new AbortController();

    try {
      const res = await fetch(`/api/chat/sessions/${sid}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: msgContent, model }),
        signal: abortRef.current.signal,
      });

      if (!res.body) throw new Error("No response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const json = line.slice(6).trim();
          if (!json) continue;
          try {
            const event = JSON.parse(json) as { type: string; text?: string; messageId?: string; message?: string };
            if (event.type === "chunk" && event.text) {
              setMessages((prev) =>
                prev.map((m) => m.id === assistantMsgId ? { ...m, content: m.content + event.text! } : m)
              );
            } else if (event.type === "done" && event.messageId) {
              setMessages((prev) =>
                prev.map((m) => m.id === assistantMsgId ? { ...m, id: event.messageId! } : m)
              );
              loadSessions();
            } else if (event.type === "error") {
              setMessages((prev) =>
                prev.map((m) => m.id === assistantMsgId ? { ...m, content: event.message ?? "Something went wrong." } : m)
              );
            }
          } catch { /* skip malformed */ }
        }
      }
    } catch (err) {
      if ((err as Error)?.name !== "AbortError") {
        setMessages((prev) =>
          prev.map((m) => m.id === assistantMsgId ? { ...m, content: "Something went wrong. Please try again." } : m)
        );
      }
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }

  async function startEdit(msg: ChatMessage) {
    setEditingMsgId(msg.id);
    setEditingContent(msg.content);
  }

  async function confirmEdit(msg: ChatMessage) {
    if (!activeSessionId || !editingContent.trim()) return;

    // Truncate messages from this point in the DB
    await fetch(`/api/chat/sessions/${activeSessionId}/messages`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fromMessageId: msg.id }),
    });

    // Remove this message and everything after from the UI
    const idx = messages.findIndex((m) => m.id === msg.id);
    setMessages((prev) => prev.slice(0, idx));
    setEditingMsgId(null);

    // Re-send with edited content
    await sendMessage(editingContent.trim(), activeSessionId);
  }

  function cancelEdit() {
    setEditingMsgId(null);
    setEditingContent("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function autoResize(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  return (
    <div className="flex h-[calc(100vh-56px)] overflow-hidden">
      {/* Sidebar */}
      <aside
        className={cn(
          "flex flex-col border-r transition-all duration-200 shrink-0",
          sidebarOpen ? "w-64" : "w-0 overflow-hidden border-0"
        )}
        style={{ backgroundColor: "var(--background)" }}
      >
        <div className="flex items-center justify-between px-3 py-3 border-b shrink-0">
          <span className="text-sm font-semibold">Conversations</span>
          <button
            onClick={newSession}
            className="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          >
            <Plus className="h-3.5 w-3.5" />
            New
          </button>
        </div>
        <div className="flex-1 overflow-y-auto py-1">
          {sessions.length === 0 ? (
            <p className="px-3 py-4 text-xs text-muted-foreground text-center">No conversations yet</p>
          ) : (
            sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => openSession(s)}
                className={cn(
                  "group flex items-start gap-2 px-3 py-2.5 cursor-pointer transition-colors rounded-md mx-1",
                  s.id === activeSessionId ? "text-white" : "text-foreground hover:bg-muted"
                )}
                style={s.id === activeSessionId ? { backgroundColor: "#FE5000" } : {}}
              >
                <MessageSquare className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium truncate">{s.title ?? "New conversation"}</p>
                  <p className={cn("text-[10px]", s.id === activeSessionId ? "text-orange-100" : "text-muted-foreground")}>
                    {formatRelative(s.updated_at)}
                  </p>
                </div>
                <button
                  onClick={(e) => deleteSession(s.id, e)}
                  className={cn(
                    "shrink-0 opacity-0 group-hover:opacity-100 transition-opacity rounded p-0.5",
                    s.id === activeSessionId ? "hover:bg-orange-700" : "hover:bg-muted-foreground/20"
                  )}
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Chat area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center gap-3 border-b px-4 py-3 shrink-0">
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          >
            {sidebarOpen ? <X className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}
          </button>
          <span className="text-sm font-medium truncate">
            {activeSession?.title ?? (activeSessionId ? "New conversation" : "Ananas AI Chat")}
          </span>
          {activeSessionId && (
            <div className="ml-auto">
              <ModelBadge modelId={activeSession?.model ?? model} />
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
          {!activeSessionId ? (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
              <div className="h-12 w-12 rounded-full flex items-center justify-center" style={{ backgroundColor: "#FE5000" }}>
                <MessageSquare className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="font-semibold text-lg">Ananas AI Chat</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Ask about marketing performance, campaigns, or data insights
                </p>
              </div>
              <button
                onClick={() => sendMessage()}
                className="mt-2 rounded-full px-5 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90"
                style={{ backgroundColor: "#FE5000" }}
              >
                Start a conversation
              </button>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full gap-2 text-center text-muted-foreground">
              <MessageSquare className="h-8 w-8 opacity-30" />
              <p className="text-sm">Ask anything about Ananas marketing data</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={cn("flex group", msg.role === "user" ? "justify-end" : "justify-start")}>
                <div className="flex flex-col gap-1 max-w-[75%]">
                  {editingMsgId === msg.id ? (
                    <div className="flex flex-col gap-2">
                      <textarea
                        value={editingContent}
                        onChange={(e) => setEditingContent(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); confirmEdit(msg); }
                          if (e.key === "Escape") cancelEdit();
                        }}
                        rows={3}
                        autoFocus
                        className="rounded-xl border px-4 py-3 text-sm bg-background focus:outline-none focus:ring-2 resize-none"
                        style={{ minWidth: 260 }}
                      />
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={cancelEdit}
                          className="px-3 py-1 text-xs rounded-md border hover:bg-muted transition-colors"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => confirmEdit(msg)}
                          className="px-3 py-1 text-xs rounded-md text-white transition-opacity hover:opacity-90"
                          style={{ backgroundColor: "#FE5000" }}
                        >
                          Send edit
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div
                      className={cn(
                        "rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap",
                        msg.role === "user" ? "text-white" : "bg-muted text-foreground"
                      )}
                      style={msg.role === "user" ? { backgroundColor: "#FE5000" } : {}}
                    >
                      {msg.content || (
                        <span className="inline-flex items-center gap-1 text-muted-foreground italic text-xs">
                          <span className="animate-pulse">Thinking</span>
                          <span className="animate-bounce">.</span>
                          <span className="animate-bounce" style={{ animationDelay: "0.1s" }}>.</span>
                          <span className="animate-bounce" style={{ animationDelay: "0.2s" }}>.</span>
                        </span>
                      )}
                    </div>
                  )}
                  {msg.role === "user" && editingMsgId !== msg.id && !streaming && (
                    <button
                      onClick={() => startEdit(msg)}
                      className="self-end flex items-center gap-1 px-2 py-0.5 text-[10px] text-muted-foreground opacity-0 group-hover:opacity-100 hover:text-foreground transition-all rounded"
                    >
                      <Pencil className="h-2.5 w-2.5" />
                      Edit
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="shrink-0 border-t px-4 py-3">
          <div className="flex items-end gap-2 rounded-2xl border bg-background px-4 py-2 focus-within:ring-2 focus-within:ring-orange-500/30">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={autoResize}
              onKeyDown={handleKeyDown}
              placeholder={activeSessionId ? "Ask anything..." : "Start a new conversation..."}
              rows={1}
              disabled={streaming}
              className="flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted-foreground disabled:opacity-50 py-1"
              style={{ maxHeight: 160 }}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || streaming}
              className="mb-1 shrink-0 rounded-full h-8 w-8 flex items-center justify-center text-white disabled:opacity-40 transition-opacity hover:opacity-90"
              style={{ backgroundColor: "#FE5000" }}
            >
              <Send className="h-3.5 w-3.5" />
            </button>
          </div>
          <div className="mt-2 flex items-center justify-between">
            <ModelPicker value={model} onChange={handleModelChange} />
            <p className="text-[10px] text-muted-foreground">Enter to send, Shift+Enter for new line</p>
          </div>
        </div>
      </div>
    </div>
  );
}
