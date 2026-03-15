"""Ananas internal API integration — api.ananas.rs.

Covers the same data surface exposed by the employee portal:
orders, products, shipments, invoices, discounts, and supplier info.

Required env vars:
  ANANAS_API_CLIENT_ID      - OAuth2 client ID (CLIENT_CREDENTIALS grant)
  ANANAS_API_CLIENT_SECRET  - OAuth2 client secret

Optional:
  ANANAS_API_BASE_URL       - defaults to https://api.ananas.rs
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import requests

from ananas_ai.integrations.base import BaseIntegration
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

_DEFAULT_BASE = "https://api.ananas.rs"
_TOKEN_PATH = "/iam/api/v1/auth/token"
_TOKEN_TTL_BUFFER = 60  # seconds before expiry to refresh


class AnanasAPIClient:
    """Low-level authenticated client for api.ananas.rs.

    Handles CLIENT_CREDENTIALS token acquisition and automatic refresh.
    """

    def __init__(self, client_id: str, client_secret: str, base_url: str = _DEFAULT_BASE) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self._token: str | None = None
        self._token_expires_at: float = 0.0
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def _acquire_token(self) -> None:
        url = f"{self.base_url}{_TOKEN_PATH}"
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
            "grantType": "CLIENT_CREDENTIALS",
        }
        resp = self._session.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        self._token = data["accessToken"]
        # expires_in is in seconds; default 3600 if not present
        expires_in = data.get("expiresIn", 3600)
        self._token_expires_at = datetime.now(timezone.utc).timestamp() + expires_in
        logger.debug("ananas_api: token acquired, expires_in=%s", expires_in)

    def _ensure_token(self) -> None:
        now = datetime.now(timezone.utc).timestamp()
        if self._token is None or now >= self._token_expires_at - _TOKEN_TTL_BUFFER:
            self._acquire_token()

    def get(self, path: str, params: dict | None = None) -> Any:
        self._ensure_token()
        url = f"{self.base_url}{path}"
        resp = self._session.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, payload: dict) -> Any:
        self._ensure_token()
        url = f"{self.base_url}{path}"
        resp = self._session.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()


class AnanasAPIIntegration(BaseIntegration):
    """Fetch commercial and operational data from the Ananas internal API.

    This integration is intentionally read-only — it never writes to
    business systems (ADR-001 compliance).

    Returns a dict with:
      orders       - order volume and GMV summary for the date range
      top_products - top-selling products by revenue
      shipments    - shipment status breakdown
      discounts    - active discount campaigns
      suppliers    - top supplier revenue contributions
    """

    name = "ananas_api"

    def is_configured(self) -> bool:
        return bool(
            os.environ.get("ANANAS_API_CLIENT_ID") and os.environ.get("ANANAS_API_CLIENT_SECRET")
        )

    def _client(self) -> AnanasAPIClient:
        return AnanasAPIClient(
            client_id=os.environ["ANANAS_API_CLIENT_ID"],
            client_secret=os.environ["ANANAS_API_CLIENT_SECRET"],
            base_url=os.environ.get("ANANAS_API_BASE_URL", _DEFAULT_BASE),
        )

    def fetch(self, date_from: str, date_to: str) -> dict:
        client = self._client()

        result: dict[str, Any] = {
            "date_from": date_from,
            "date_to": date_to,
        }

        # ── Orders ──────────────────────────────────────────────────────────
        try:
            orders_data = client.get(
                "/order/api/v1/orders",
                params={
                    "dateFrom": date_from,
                    "dateTo": date_to,
                    "page": 0,
                    "size": 500,
                },
            )
            orders = (
                orders_data.get("content", orders_data)
                if isinstance(orders_data, dict)
                else orders_data
            )
            if isinstance(orders, list):
                total_orders = len(orders)
                total_gmv = sum(float(o.get("totalPrice", o.get("total", 0)) or 0) for o in orders)
                status_counts: dict[str, int] = {}
                for o in orders:
                    status = o.get("status", o.get("orderStatus", "UNKNOWN"))
                    status_counts[status] = status_counts.get(status, 0) + 1
                result["orders"] = {
                    "total_orders": total_orders,
                    "total_gmv": round(total_gmv, 2),
                    "status_breakdown": status_counts,
                }
            else:
                result["orders"] = orders_data
        except Exception as exc:
            logger.warning("ananas_api: orders fetch failed: %s", exc)
            result["orders"] = {}

        # ── Top products ─────────────────────────────────────────────────────
        try:
            products_data = client.get(
                "/product/api/v1/products",
                params={
                    "dateFrom": date_from,
                    "dateTo": date_to,
                    "sort": "revenue,desc",
                    "page": 0,
                    "size": 20,
                },
            )
            products = (
                products_data.get("content", [])
                if isinstance(products_data, dict)
                else products_data
            )
            result["top_products"] = [
                {
                    "id": p.get("id"),
                    "name": p.get("name", p.get("title", "")),
                    "sku": p.get("sku", p.get("externalId", "")),
                    "revenue": round(float(p.get("revenue", 0) or 0), 2),
                    "units_sold": int(p.get("unitsSold", p.get("quantity", 0)) or 0),
                }
                for p in (products[:20] if isinstance(products, list) else [])
            ]
        except Exception as exc:
            logger.warning("ananas_api: products fetch failed: %s", exc)
            result["top_products"] = []

        # ── Shipments ────────────────────────────────────────────────────────
        try:
            shipments_data = client.get(
                "/shipment/api/v1/shipments",
                params={
                    "dateFrom": date_from,
                    "dateTo": date_to,
                    "page": 0,
                    "size": 500,
                },
            )
            shipments = (
                shipments_data.get("content", shipments_data)
                if isinstance(shipments_data, dict)
                else shipments_data
            )
            if isinstance(shipments, list):
                shipment_statuses: dict[str, int] = {}
                for s in shipments:
                    status = s.get("status", s.get("shipmentStatus", "UNKNOWN"))
                    shipment_statuses[status] = shipment_statuses.get(status, 0) + 1
                result["shipments"] = {
                    "total": len(shipments),
                    "status_breakdown": shipment_statuses,
                }
            else:
                result["shipments"] = shipments_data
        except Exception as exc:
            logger.warning("ananas_api: shipments fetch failed: %s", exc)
            result["shipments"] = {}

        # ── Active discounts ─────────────────────────────────────────────────
        try:
            discounts_data = client.get(
                "/discount/api/v1/discounts",
                params={"page": 0, "size": 50, "active": "true"},
            )
            discounts = (
                discounts_data.get("content", [])
                if isinstance(discounts_data, dict)
                else discounts_data
            )
            result["active_discounts"] = [
                {
                    "id": d.get("id"),
                    "name": d.get("name", ""),
                    "type": d.get("type", d.get("discountType", "")),
                    "value": d.get("value", d.get("discountValue", 0)),
                    "valid_from": d.get("validFrom", d.get("startDate", "")),
                    "valid_to": d.get("validTo", d.get("endDate", "")),
                    "usage_count": d.get("usageCount", 0),
                }
                for d in (discounts[:20] if isinstance(discounts, list) else [])
            ]
        except Exception as exc:
            logger.warning("ananas_api: discounts fetch failed: %s", exc)
            result["active_discounts"] = []

        # ── Supplier / wholesaler revenue ────────────────────────────────────
        try:
            suppliers_data = client.get(
                "/supplier/api/v1/suppliers",
                params={
                    "dateFrom": date_from,
                    "dateTo": date_to,
                    "sort": "revenue,desc",
                    "page": 0,
                    "size": 20,
                },
            )
            suppliers = (
                suppliers_data.get("content", [])
                if isinstance(suppliers_data, dict)
                else suppliers_data
            )
            result["top_suppliers"] = [
                {
                    "id": s.get("id"),
                    "name": s.get("name", s.get("companyName", "")),
                    "revenue": round(float(s.get("revenue", 0) or 0), 2),
                    "order_count": int(s.get("orderCount", s.get("orders", 0)) or 0),
                }
                for s in (suppliers[:20] if isinstance(suppliers, list) else [])
            ]
        except Exception as exc:
            logger.warning("ananas_api: suppliers fetch failed: %s", exc)
            result["top_suppliers"] = []

        logger.info(
            "ananas_api: fetched orders=%s products=%d discounts=%d suppliers=%d",
            result.get("orders", {}).get("total_orders", "?"),
            len(result.get("top_products", [])),
            len(result.get("active_discounts", [])),
            len(result.get("top_suppliers", [])),
        )

        return result
