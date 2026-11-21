import asyncio
import json
import re
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

from playwright.async_api import async_playwright


SITE_URL = "http://127.0.0.1:4173/index.html"
API_URL = "http://127.0.0.1:8000"
SESSION_KEY = "bongora.chat.session.v1"
TEST_MESSAGE = "Live Playwright Phase 3 QA"
ROOT = Path(__file__).resolve().parents[1]


class QuietRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format_string, *args):
        pass


async def main():
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

            await page.goto(SITE_URL, wait_until="networkidle")
            launcher = page.get_by_role("button", name=re.compile("Bongora chat"))
            await launcher.click()

            session_token = await page.evaluate(
                "(key) => window.localStorage.getItem(key)", SESSION_KEY
            )
            assert re.fullmatch(
                r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
                session_token or "",
                re.IGNORECASE,
            ), "Live widget did not provide a valid session token."

            input_box = page.get_by_role("textbox", name="আপনার বার্তা")
            await input_box.fill(TEST_MESSAGE)
            await page.get_by_role("button", name="বার্তা পাঠান").click()
            await page.locator(".message--assistant").nth(1).wait_for(timeout=15000)

            with urlopen(
                f"{API_URL}/api/chat/sessions/{session_token}/messages",
                timeout=10,
            ) as response:
                history = json.loads(response.read().decode("utf-8"))

            messages = history["messages"]
            assert any(
                item["sender_type"] == "customer" and item["message"] == TEST_MESSAGE
                for item in messages
            ), "Live customer message was not stored in MySQL."
            assert any(
                item["sender_type"] == "assistant" and item["message"].strip()
                for item in messages
            ), "Live assistant reply was not stored in MySQL."
            assert not page_errors, f"Uncaught page errors: {page_errors}"
            assert not console_errors, f"Browser console errors: {console_errors}"

            print("PASS: live widget sent a message through the FastAPI endpoint.")
            print("PASS: live session and both message directions persisted in MySQL.")
            print("PASS: live widget browser had zero console or uncaught page errors.")
        finally:
            await browser.close()


handler = partial(QuietRequestHandler, directory=str(ROOT))
server = ThreadingHTTPServer(("127.0.0.1", 4173), handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    asyncio.run(main())
finally:
    server.shutdown()
    server.server_close()
    thread.join()
