import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import {
  getChatSession,
  getChatMessages,
  addChatMessage,
  updateChatSessionTitle,
} from "@/lib/db-portal";
import Anthropic from "@anthropic-ai/sdk";
import { randomUUID } from "crypto";

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const SYSTEM_PROMPT = `You are the Ananas AI assistant — an internal marketing intelligence tool for Ananas, a Macedonian e-commerce marketplace.

You have deep context about:
- Ananas marketing team: 8 people (2 designers, 3 performance, 1 content/social, 1 CRM, 1 TBD)
- Key metrics: GA4 sessions, revenue, ROAS, cart abandonment, Trustpilot rating (currently 2.0 - critical)
- Integrations: GA4 (live), Google Ads (4 accounts, 14 campaigns), Meta Ads (20 campaigns), Trustpilot, Google Business
- Business context: 250k+ products, no Google Shopping campaigns, coupon-dependent sales, no email lifecycle automations
- Internal tools: Jira, Asana, Confluence, Teams, SharePoint, Outlook

Be concise, data-driven, and actionable. When giving advice, relate it to Ananas's specific situation.`;

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await auth();
  const email = (session?.user as { email?: string } | undefined)?.email;
  if (!email) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { id } = await params;
  const chatSession = getChatSession(id, email);
  if (!chatSession) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const messages = getChatMessages(id);
  return NextResponse.json({ messages });
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

  const body = await request.json().catch(() => null) as { content?: string } | null;
  const userContent = body?.content?.trim();
  if (!userContent) return NextResponse.json({ error: "Missing content" }, { status: 400 });

  // Save user message
  const userMsgId = randomUUID();
  addChatMessage({ id: userMsgId, session_id: id, role: "user", content: userContent, tokens_in: null, tokens_out: null, cost_usd: null });

  // Build history for Anthropic
  const history = getChatMessages(id);
  const anthropicMessages: Anthropic.MessageParam[] = history.map((m) => ({
    role: m.role as "user" | "assistant",
    content: m.content,
  }));

  // Auto-title on first user message
  if (history.filter((m) => m.role === "user").length === 1 && !chatSession.title) {
    const title = userContent.slice(0, 60) + (userContent.length > 60 ? "..." : "");
    updateChatSessionTitle(id, title);
  }

  // Stream response via SSE
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      function send(data: string) {
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      }

      try {
        let fullText = "";
        let inputTokens = 0;
        let outputTokens = 0;

        const response = await anthropic.messages.stream({
          model: "claude-sonnet-4-6",
          max_tokens: 4096,
          system: SYSTEM_PROMPT,
          messages: anthropicMessages,
        });

        for await (const event of response) {
          if (
            event.type === "content_block_delta" &&
            event.delta.type === "text_delta"
          ) {
            const chunk = event.delta.text;
            fullText += chunk;
            send(JSON.stringify({ type: "chunk", text: chunk }));
          } else if (event.type === "message_delta" && event.usage) {
            outputTokens = event.usage.output_tokens ?? 0;
          } else if (event.type === "message_start" && event.message.usage) {
            inputTokens = event.message.usage.input_tokens ?? 0;
          }
        }

        // Cost estimate: claude-sonnet-4-6 $3/1M in, $15/1M out
        const costUsd = inputTokens * 0.000003 + outputTokens * 0.000015;

        const assistantMsgId = randomUUID();
        addChatMessage({
          id: assistantMsgId,
          session_id: id,
          role: "assistant",
          content: fullText,
          tokens_in: inputTokens,
          tokens_out: outputTokens,
          cost_usd: costUsd,
        });

        send(JSON.stringify({ type: "done", messageId: assistantMsgId, tokens_in: inputTokens, tokens_out: outputTokens }));
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Stream error";
        send(JSON.stringify({ type: "error", message: msg }));
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
