from report_service import OrderUpdate, email_order_report


def test_order_report_sends_customer_update(monkeypatch):
    seen = {}
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    monkeypatch.setattr("report_service._send", lambda payload: seen.update(payload) or {"message_id": "m-1"})
    result = email_order_report(OrderUpdate("A-42", "buyer@example.com", "Mina", 2599, "shipped"))
    assert result["message_id"] == "m-1"
    assert seen["to"] == "buyer@example.com"
    assert "Download your PDF report" in seen["html"]
    assert "application/pdf" in seen["html"]

