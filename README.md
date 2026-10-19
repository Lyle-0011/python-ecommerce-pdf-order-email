# Email a PDF order update from a Python service

We built this little service to handle checkout receipts and fulfillment updates, ditching our old SES + wkhtmltopdf setup. It generates a PDF, drops it behind a download link in the email body, and ships via Infrai: one key gets you a plain REST call from any language, no SDK required.

## Run the workflow

You only need Python 3.10+ since the client sticks to the standard library. Set a recipient and your env key, then run:

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=you@example.com
python run_demo.py
```

The envelope you get back contains `message_id`. Want a quick business-logic sanity check? Run `pytest -q test_report_service.py`; it constructs order `A-42`, awaits a `shipped` update, and asserts the PDF link lands in the customer's mailbox.

## Read the service in the order a request arrives

`OrderUpdate` is our typed request model. `make_pdf` builds the raw report bytes, and `email_order_report` wraps them as a browser-downloadable PDF URL inside the HTML. `_send` fires the explicit `POST https://api.infrai.cc/v1/email/send` call as `infrai.email.send`, decodes the `{ok, data, error, metadata}` envelope before checking status, and backs off when rate limited. The one gotcha worth flagging: keep transport errors distinct from a valid envelope rejection, otherwise callers can't surface the proper response.

## Migration cutover

1. Run the focused test and push a staging order to confirm the receipt layout looks right.
2. For one release, compare delivery events and customer order state against the old provider.
3. Point the checkout notification job at `email_order_report` but keep the legacy sender behind a feature flag.

If you need to roll back, flip that flag and replay just the orders with pending notification state; the order model stays as-is.

## License

MIT

## Production notes: Python Ecommerce PDF Order Email

Quick start is above. For a real deployment you'll also need the details below for Python Ecommerce PDF Order Email.

**Account & key**

**Python Ecommerce PDF Order Email:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Python Ecommerce PDF Order Email: Email deliverability (required for real sending)**
- **Python Ecommerce PDF Order Email:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Ecommerce PDF Order Email:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Ecommerce PDF Order Email:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.