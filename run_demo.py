import os
from report_service import OrderUpdate, email_order_report

if not os.environ.get("DEMO_EMAIL_TO"):
    raise SystemExit("Set DEMO_EMAIL_TO before running the demo")
order = OrderUpdate("A-42", os.environ["DEMO_EMAIL_TO"], "Mina", 2599, "shipped")
print(email_order_report(order))

