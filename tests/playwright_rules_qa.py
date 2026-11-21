import asyncio
import json
import re
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]


class QuietRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format_string, *args):
        pass


async def run_qa(site_url):
    console_errors = []
    page_errors = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--no-proxy-server", "--proxy-bypass-list=<-loopback>"],
        )
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 900})
            page.on(
                "console",
                lambda message: console_errors.append(message.text)
                if message.type == "error"
                else None,
            )
            page.on("pageerror", lambda error: page_errors.append(str(error)))

            async def mock_rules(route):
                if route.request.url.endswith("/health"):
                    await route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps({"status": "ok"}),
                    )
                    return
                if route.request.url.endswith("/api/rules/active"):
                    await route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps({
                            "rules": [
                                {
                                    "id": 1,
                                    "rule_name": "First visit welcome",
                                    "trigger_event": "on_first_visit",
                                    "action_type": "Static Message",
                                    "static_message": "Welcome from the first-visit rule.",
                                    "assigned_role": None,
                                    "trigger_config": {},
                                    "priority": 1,
                                    "is_active": True,
                                    "execution_frequency": "once_per_session",
                                },
                                {
                                    "id": 2,
                                    "rule_name": "URL preview rule",
                                    "trigger_event": "url_match",
                                    "action_type": "Static Message",
                                    "static_message": "Welcome from the URL rule.",
                                    "assigned_role": None,
                                    "trigger_config": {"url_match": "/index.html"},
                                    "priority": 2,
                                    "is_active": True,
                                    "execution_frequency": "once_per_session",
                                },
                                {
                                    "id": 3,
                                    "rule_name": "Timed rule",
                                    "trigger_event": "time_on_page",
                                    "action_type": "Static Message",
                                    "static_message": "Welcome from the timed rule.",
                                    "assigned_role": None,
                                    "trigger_config": {"delay_seconds": 0.1},
                                    "priority": 3,
                                    "is_active": True,
                                    "execution_frequency": "once_per_session",
                                },
                            ]
                        }),
                    )
                    return
                await route.continue_()

            await page.route("http://127.0.0.1:8000/**", mock_rules)
            await page.goto(site_url, wait_until="networkidle")

            await page.get_by_text(
                "Welcome from the first-visit rule.",
                exact=True,
            ).wait_for(timeout=5000)
            await page.get_by_text(
                "Welcome from the URL rule.",
                exact=True,
            ).wait_for(timeout=5000)
            await page.get_by_text(
                "Welcome from the timed rule.",
                exact=True,
            ).wait_for(timeout=5000)

            rule_bubbles = await page.get_by_text(
                re.compile("Welcome from the .* rule."),
            ).count()
            assert rule_bubbles >= 3, "Expected static rules to execute."

            await page.reload(wait_until="networkidle")
            await page.wait_for_timeout(500)
            duplicate_bubbles = await page.get_by_text(
                re.compile("Welcome from the .* rule."),
            ).count()
            assert duplicate_bubbles == 0, "Once-per-session rules executed again after reload."

            assert not page_errors, f"Uncaught page errors: {page_errors}"
            assert not console_errors, f"Browser console errors: {console_errors}"
            print("PASS: on-first-visit, URL, and timed static rules execute.")
            print("PASS: once-per-session rules do not duplicate after reload.")
            print("PASS: rule execution has zero browser console or uncaught page errors.")
        finally:
            await browser.close()


def main():
    handler = partial(QuietRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        asyncio.run(run_qa(f"http://127.0.0.1:{server.server_port}/index.html"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    main()
