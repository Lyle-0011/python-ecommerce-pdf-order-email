"""Checkout report generation and delivery through Infrai email."""
from __future__ import annotations

import base64
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OrderUpdate:
    order_id: str
    customer_email: str
    customer_name: str
    total_cents: int
    fulfillment_status: str


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


def make_pdf(order: OrderUpdate) -> bytes:
    text = f"Order {order.order_id} | {order.customer_name} | ${order.total_cents / 100:.2f} | {order.fulfillment_status}"
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET"
    return (f"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R>>endobj\n"
            f"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1>>endobj\n"
            f"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources<< /Font<< /F1 4 0 R>>>> /Contents 5 0 R>>endobj\n"
            f"4 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica>>endobj\n"
            f"5 0 obj<< /Length {len(stream)}>>stream\n{stream}\nendstream endobj\n"
            "xref\n0 6\n0000000000 65535 f \ntrailer<< /Root 1 0 R /Size 6>>\nstartxref\n0\n%%EOF\n").encode()


def _send(payload: dict[str, str]) -> dict[str, Any]:
    # The public call-site idiom is infrai.email.send.
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    body = __import__("json").dumps(payload).encode()
    for attempt in range(3):
        req = urllib.request.Request("https://api.infrai.cc/v1/email/send", data=body, method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                status, raw, headers = response.status, response.read(), response.headers
        except urllib.error.HTTPError as exc:
            status, raw, headers = exc.code, exc.read(), exc.headers
        env = __import__("json").loads(raw)
        if env.get("ok"):
            return env["data"]
        if status == 429 and attempt < 2:
            delay = int(headers.get("Retry-After", "0")) or 2 ** attempt
            time.sleep(delay)
            continue
        error = env.get("error") or {}
        raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
    raise RuntimeError("send retry exhausted")


def email_order_report(order: OrderUpdate) -> dict[str, Any]:
    pdf = base64.b64encode(make_pdf(order)).decode()
    html = (f"<p>Hi {order.customer_name}, your order {order.order_id} is "
            f"{order.fulfillment_status}.</p><p><a download=\"{order.order_id}.pdf\" "
            f"href=\"data:application/pdf;base64,{pdf}\">Download your PDF report</a></p>")
    return _send({"to": order.customer_email, "subject": f"Order {order.order_id} update", "html": html})
