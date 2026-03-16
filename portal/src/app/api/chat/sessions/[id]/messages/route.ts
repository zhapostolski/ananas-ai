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
import { getLatestOutput } from "@/lib/db";
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

function fmt(v: unknown, suffix = ""): string {
  if (v == null) return "n/a";
  return String(v) + suffix;
}

function buildSystemPrompt(): string {
  const today = new Date().toISOString().slice(0, 10);

  // Load latest outputs from all 5 agents
  const perf = getLatestOutput("performance-agent");
  const crm = getLatestOutput("crm-lifecycle-agent");
  const rep = getLatestOutput("reputation-agent");
  const ops = getLatestOutput("marketing-ops-agent");
  const brief = getLatestOutput("cross-channel-brief-agent");

  const perfJson = (perf?.output_json ?? {}) as Record<string, unknown>;
  const crmJson = (crm?.output_json ?? {}) as Record<string, unknown>;
  const repJson = (rep?.output_json ?? {}) as Record<string, unknown>;
  const opsJson = (ops?.output_json ?? {}) as Record<string, unknown>;
  const briefJson = (brief?.output_json ?? {}) as Record<string, unknown>;

  const perfSummary = (perfJson.summary ?? {}) as Record<string, unknown>;
  const ga4 = (perfJson.ga4 ?? {}) as Record<string, unknown>;
  const googleAds = (perfJson.google_ads ?? {}) as Record<string, unknown>;
  const metaAds = (perfJson.meta_ads ?? {}) as Record<string, unknown>;
  const emailKpi = ((crmJson.email ?? {}) as Record<string, unknown>);
  const lifecycle = ((crmJson.lifecycle ?? {}) as Record<string, unknown>);
  const tp = ((repJson.trustpilot ?? {}) as Record<string, unknown>);
  const gb = ((repJson.google_business ?? {}) as Record<string, unknown>);
  const tracking = ((opsJson.tracking_health ?? {}) as Record<string, unknown>);

  const perfRunAt = perf?.run_at ? String(perf.run_at).slice(0, 16) : "no data";
  const crmRunAt = crm?.run_at ? String(crm.run_at).slice(0, 16) : "no data";
  const repRunAt = rep?.run_at ? String(rep.run_at).slice(0, 16) : "no data";

  return `You are the Ananas AI assistant — an internal intelligence tool for Ananas, a Macedonian e-commerce marketplace.

Today's date: ${today}

## Team & Stack
- Marketing team: 8 people (2 designers, 3 performance marketers, 1 content/social, 1 CRM specialist, 1 TBD)
- Ad platforms: Google Ads (4 accounts, 14 campaigns), Meta Ads (20 campaigns across Facebook/Instagram)
- Internal tools: Jira, Asana, Confluence, Microsoft Teams, SharePoint, Outlook, Berry (HR)
- Business context: 250k+ active products, coupon-dependent sales (coupons mask true acquisition efficiency), no email lifecycle automations live (no cart recovery, no churn flows), Trustpilot profile not yet claimed

## Live Agent Data

### Performance (last run: ${perfRunAt})
- GA4 Revenue: ${fmt(ga4.revenue ?? perfSummary.ga4_revenue, " €")}
- GA4 Sessions: ${fmt(ga4.sessions ?? perfSummary.ga4_sessions)}
- GA4 Users: ${fmt(ga4.users)}
- Conversion Rate: ${fmt(ga4.conversion_rate_pct ?? perfSummary.ga4_conversion_rate_pct, "%")}
- Total Paid Spend: ${fmt(perfSummary.total_paid_spend, " €")}
- Blended ROAS: ${fmt(perfSummary.blended_roas, "x")}
- Google Ads Spend: ${fmt(googleAds.total_spend, " €")} | Impressions: ${fmt(googleAds.total_impressions)} | Clicks: ${fmt(googleAds.total_clicks)} | CPC: ${fmt(googleAds.avg_cpc, " €")}
- Meta Ads Spend: ${fmt(metaAds.total_spend, " €")} | Impressions: ${fmt(metaAds.total_impressions)} | Clicks: ${fmt(metaAds.total_clicks)} | CPC: ${fmt(metaAds.avg_cpc, " €")} | CPM: ${fmt(metaAds.avg_cpm, " €")}
- Meta ROAS: ${fmt(metaAds.roas, "x")} | Google ROAS: ${fmt(googleAds.roas, "x")}
${perf?.summary_text ? `\nPerformance summary: ${perf.summary_text}` : ""}

### CRM & Lifecycle (last run: ${crmRunAt})
- Cart Abandonment Rate: ${fmt(emailKpi.cart_abandonment_rate, "%")}
- Cart Recovery Rate: ${fmt(emailKpi.cart_recovery_rate, "%")} (0% — no automation live)
- Email Open Rate: ${fmt(emailKpi.open_rate, "%")}
- Revenue per Send: ${fmt(emailKpi.revenue_per_send, " €")}
- Active Subscribers (90d): ${fmt(emailKpi.active_subscribers)}
- Repeat Purchase Rate: ${fmt(lifecycle.repeat_purchase_rate, "%")}
- Churn Rate (30d): ${fmt(lifecycle.churn_rate_30d, "%")}
- LTV:CAC Ratio: ${fmt(lifecycle.ltv_cac_ratio, ":1")}
- AOV: ${fmt(lifecycle.aov, " €")}
${crm?.summary_text ? `\nCRM summary: ${crm.summary_text}` : ""}

### Reputation (last run: ${repRunAt})
- Trustpilot Rating: ${fmt(tp.average_rating, " / 5.0")} (CRITICAL — target >4.0)
- Trustpilot Reviews: ${fmt(tp.review_count)} | Response Rate: ${fmt(tp.response_rate, "%")} | Profile Claimed: ${tp.claimed ? "Yes" : "No — action required"}
- Google Business Rating: ${fmt(gb.average_rating, " / 5.0")} | Reviews: ${fmt(gb.total_reviews)} | Unanswered: ${fmt(gb.unanswered_reviews)}
${rep?.summary_text ? `\nReputation summary: ${rep.summary_text}` : ""}

### Marketing Ops
- Tracking Status: ${fmt(tracking.status)}
- GA4 Sessions (today): ${fmt(tracking.ga4_sessions)}
${ops?.summary_text ? `\nOps summary: ${ops.summary_text}` : ""}

### Cross-Channel Brief
${brief?.summary_text ?? briefJson.analysis ?? "No brief available yet."}

## Instructions
- Answer based on the live data above — do not say you lack access to Meta Ads, GA4, or other data shown here
- Be specific and data-driven; cite actual numbers from the data above
- If a metric shows "n/a", say the agent hasn't run yet or data wasn't collected in the last run
- Relate insights to Ananas's specific challenges: coupon dependency, Trustpilot 2.0 rating, no Google Shopping, no lifecycle automations
- Keep answers concise and direct
- Do not use markdown formatting (no **, ##, *, or backticks). Write in plain text with natural line breaks. Use short paragraphs. For lists, use plain dashes or numbers.`;
}

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

      const systemPrompt = buildSystemPrompt();
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
            { role: "system", content: systemPrompt },
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
          system: systemPrompt,
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
