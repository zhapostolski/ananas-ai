import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import {
  getChatSession,
  getChatMessages,
  addChatMessage,
  updateChatSessionTitle,
  updateChatSessionModel,
  truncateChatMessagesFrom,
} from "@/lib/db-portal";
import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";
import { randomUUID } from "crypto";

function getAnthropic() {
  return new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
}
function getOpenAI() {
  return new OpenAI({ apiKey: process.env.OPENAI_API_KEY ?? "" });
}

const CLAUDE_MODELS = ["claude-sonnet-4-6", "claude-opus-4-6", "claude-haiku-4-5"] as const;
const GPT_MODELS = ["gpt-4o", "gpt-4o-mini"] as const;
type SupportedModel = (typeof CLAUDE_MODELS)[number] | (typeof GPT_MODELS)[number];

const SYSTEM_PROMPT = `You are the Ananas AI assistant — an internal intelligence tool for Ananas, a Macedonian e-commerce marketplace.

You have deep context about the Ananas marketing team:
- Team: 8 people (2 designers, 3 performance marketers, 1 content/social, 1 CRM specialist, 1 TBD)
- Key metrics tracked: GA4 sessions, revenue (GMV), ROAS, POAS, cart abandonment rate, Trustpilot rating (currently 2.0 — critical issue), repeat purchase rate
- Ad platforms: Google Ads (4 accounts, 14 campaigns), Meta Ads (20 campaigns across Facebook/Instagram)
- Other integrations: Trustpilot, Google Business Reviews, email CRM
- Business context: 250k+ active products, coupon-dependent sales (coupons drive a large portion of revenue — masks true acquisition efficiency), no email lifecycle automations currently live (no cart recovery, no churn flows), Trustpilot profile not yet claimed
- Internal tools: Jira, Asana, Confluence, Microsoft Teams, SharePoint, Outlook, Berry (HR)
- GA4 (live): ~464k sessions/month, ~215k users/month, ~€13.4M revenue/month

When answering questions about marketing performance, campaigns, or metrics:
- Be specific, data-driven, and actionable
- When date ranges are requested (e.g. "last week", "yesterday", "March"), acknowledge the range clearly and answer based on what you know or explain what data would be needed
- Relate advice to Ananas's specific situation (coupon dependency, reputation issues, missing Google Shopping, no lifecycle automations)
- Keep answers concise and direct — avoid filler

Today's date context: use it for relative date calculations when users mention "yesterday", "last week", "this month", etc.`;

function isValidModel(m: string): m is SupportedModel {
  return ([...CLAUDE_MODELS, ...GPT_MODELS] as string[]).includes(m);
}

// Truncate messages from a given message ID (for edit/branch)
export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  const email = (session?.user as { email?: string } | undefined)?.email;
  if (!email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { id } = await params;
  const chatSession = getChatSession(id, email);
  if (!chatSession) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const body = await request.json().catch(() => null) as { fromMessageId?: string } | null;
  if (!body?.fromMessageId) return NextResponse.json({ error: "Missing fromMessageId" }, { status: 400 });

  truncateChatMessagesFrom(id, body.fromMessageId);
  return NextResponse.json({ ok: true });
}

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  const email = (session?.user as { email?: string } | undefined)?.email;
  if (!email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { id } = await params;
  const chatSession = getChatSession(id, email);
  if (!chatSession) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const body = await request.json().catch(() => null) as { content?: string; model?: string } | null;
  const userContent = body?.content?.trim();
  if (!userContent) return NextResponse.json({ error: "Missing content" }, { status: 400 });

  const requestedModel = body?.model && isValidModel(body.model) ? body.model : chatSession.model;

  // Update session model if changed
  if (requestedModel !== chatSession.model) {
    updateChatSessionModel(id, requestedModel);
  }

  // Save user message
  const userMsgId = randomUUID();
  addChatMessage({ id: userMsgId, session_id: id, role: "user", content: userContent, tokens_in: null, tokens_out: null, cost_usd: null });

  // Build history
  const history = getChatMessages(id);

  // Auto-title on first user message
  if (history.filter((m) => m.role === "user").length === 1 && !chatSession.title) {
    updateChatSessionTitle(id, userContent.slice(0, 60) + (userContent.length > 60 ? "..." : ""));
  }

  const encoder = new TextEncoder();
  const { readable, writable } = new TransformStream<Uint8Array, Uint8Array>();
  const writer = writable.getWriter();

  function send(data: string) {
    return writer.write(encoder.encode(`data: ${data}\n\n`));
  }

  void (async () => {
    try {
      let fullText = "";
      let inputTokens = 0;
      let outputTokens = 0;

      const isGpt = (GPT_MODELS as readonly string[]).includes(requestedModel);

      if (isGpt) {
        const gptMessages = history.map((m) => ({
          role: m.role as "user" | "assistant",
          content: m.content,
        }));

        const stream = await getOpenAI().chat.completions.create({
          model: requestedModel,
          stream: true,
          messages: [
            { role: "system", content: SYSTEM_PROMPT },
            ...gptMessages,
          ],
        });

        for await (const chunk of stream) {
          const text = chunk.choices[0]?.delta?.content ?? "";
          if (text) {
            fullText += text;
            await send(JSON.stringify({ type: "chunk", text }));
          }
          if (chunk.usage) {
            inputTokens = chunk.usage.prompt_tokens ?? 0;
            outputTokens = chunk.usage.completion_tokens ?? 0;
          }
        }

        // GPT-4o pricing: $2.50/$10.00 per 1M tokens; gpt-4o-mini: $0.15/$0.60
        const isGpt4o = requestedModel === "gpt-4o";
        const costUsd = isGpt4o
          ? inputTokens * 0.0000025 + outputTokens * 0.00001
          : inputTokens * 0.00000015 + outputTokens * 0.0000006;

        const assistantMsgId = randomUUID();
        addChatMessage({ id: assistantMsgId, session_id: id, role: "assistant", content: fullText, tokens_in: inputTokens, tokens_out: outputTokens, cost_usd: costUsd });
        await send(JSON.stringify({ type: "done", messageId: assistantMsgId, tokens_in: inputTokens, tokens_out: outputTokens }));
      } else {
        const anthropicMessages: Anthropic.MessageParam[] = history.map((m) => ({
          role: m.role as "user" | "assistant",
          content: m.content,
        }));

        const claudeStream = getAnthropic().messages.stream({
          model: requestedModel,
          max_tokens: 4096,
          system: SYSTEM_PROMPT,
          messages: anthropicMessages,
        });

        for await (const event of claudeStream) {
          if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
            fullText += event.delta.text;
            await send(JSON.stringify({ type: "chunk", text: event.delta.text }));
          } else if (event.type === "message_start" && event.message.usage) {
            inputTokens = event.message.usage.input_tokens ?? 0;
          } else if (event.type === "message_delta" && event.usage) {
            outputTokens = event.usage.output_tokens ?? 0;
          }
        }

        // claude-sonnet-4-6: $3/$15 per 1M; claude-opus-4-6: $5/$25; claude-haiku-4-5: $1/$5
        const rates: Record<string, [number, number]> = {
          "claude-sonnet-4-6": [0.000003, 0.000015],
          "claude-opus-4-6": [0.000005, 0.000025],
          "claude-haiku-4-5": [0.000001, 0.000005],
        };
        const [inRate, outRate] = rates[requestedModel] ?? [0.000003, 0.000015];
        const costUsd = inputTokens * inRate + outputTokens * outRate;

        const assistantMsgId = randomUUID();
        addChatMessage({ id: assistantMsgId, session_id: id, role: "assistant", content: fullText, tokens_in: inputTokens, tokens_out: outputTokens, cost_usd: costUsd });
        await send(JSON.stringify({ type: "done", messageId: assistantMsgId, tokens_in: inputTokens, tokens_out: outputTokens }));
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Stream error";
      await send(JSON.stringify({ type: "error", message: msg }));
    } finally {
      await writer.close();
    }
  })();

  return new Response(readable, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
