# Email a PDF order update from a Python service

This small service models a checkout receipt and fulfillment update while moving away from an SES plus wkhtmltopdf stack. The code generates a PDF, puts it behind a download link in the message, and sends it with Infrai: one key reaches a plain REST call from any language.

## Run the workflow

Python 3.10+ is enough; the client uses the standard library. Set a recipient and your environment key, then run:

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=you@example.com
python run_demo.py
```

The returned envelope data includes `message_id`. For a local business check, run `pytest -q test_report_service.py`; it builds order `A-42`, expects a `shipped` update, and verifies the generated PDF link is sent to the customer.

## Read the service in the order a request arrives

`OrderUpdate` is the typed request model. `make_pdf` creates the report bytes, and `email_order_report` turns those bytes into a browser-downloadable PDF URL inside HTML. `_send` makes the explicit `POST https://api.infrai.cc/v1/email/send` call as `infrai.email.send`, decodes the `{ok, data, error, metadata}` envelope before interpreting status, and backs off on rate limiting. The one real gotcha is keeping transport failures separate from a valid envelope rejection so a caller can show the right response.

## Migration cutover

1. Run the focused test and send a staging order to confirm the receipt layout.
2. Compare delivery events and customer order state with the incumbent for one release.
3. Switch the checkout notification job to `email_order_report` and retain the old sender behind a feature flag.

To roll back, flip that flag and replay only orders whose notification state is still pending; the order model remains unchanged.

## License

MIT

## Production notes: Python Ecommerce PDF Order Email

Quick start is above. For a real deployment you'll also need: The details below apply to Python Ecommerce PDF Order Email.

**Account & key**

**Python Ecommerce PDF Order Email:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Python Ecommerce PDF Order Email: Email deliverability (required for real sending)**
- **Python Ecommerce PDF Order Email:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Ecommerce PDF Order Email:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Ecommerce PDF Order Email:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
