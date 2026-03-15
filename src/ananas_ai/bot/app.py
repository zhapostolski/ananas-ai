"""Ananas AI Teams bot -- aiohttp server entry point.

Listens on port 3978 for Bot Framework activities from Teams.
nginx proxies /api/messages -> localhost:3978 (HTTPS termination handled by nginx).

Required env vars:
  BOT_APP_ID      -- Microsoft App ID from Azure Bot registration
  BOT_APP_PASSWORD -- Microsoft App Password (client secret)

Run:
  python -m ananas_ai.bot.app
  # or via PM2:
  pm2 start "python -m ananas_ai.bot.app" --name ananas-bot
"""

from __future__ import annotations

import os
from http import HTTPStatus

from aiohttp import web  # type: ignore[import]
from botbuilder.core import (  # type: ignore[import]
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
)
from botbuilder.schema import Activity  # type: ignore[import]

from ananas_ai.bot.handler import AnanasBot
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SETTINGS = BotFrameworkAdapterSettings(
    app_id=os.environ.get("BOT_APP_ID", ""),
    app_password=os.environ.get("BOT_APP_PASSWORD", ""),
)
ADAPTER = BotFrameworkAdapter(SETTINGS)
BOT = AnanasBot()


async def on_error(context, error: Exception) -> None:
    logger.error("bot: unhandled error: %s", error)
    await context.send_activity("An unexpected error occurred. Please try again.")


ADAPTER.on_turn_error = on_error


async def messages(req: web.Request) -> web.Response:
    if req.content_type != "application/json":
        return web.Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return web.json_response(data=response.body, status=response.status)
    return web.Response(status=HTTPStatus.CREATED)


async def health(req: web.Request) -> web.Response:  # noqa: ARG001
    return web.json_response({"status": "ok", "service": "ananas-bot"})


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/api/messages", messages)
    app.router.add_get("/health", health)
    return app


def main() -> None:
    port = int(os.environ.get("BOT_PORT", 3978))
    logger.info("Starting Ananas Teams bot on port %d", port)
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
