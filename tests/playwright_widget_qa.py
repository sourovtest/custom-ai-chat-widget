import asyncio
import json
import re
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
SESSION_KEY = "bongora.chat.session.v1"
SESSION_CREATED_AT_KEY = "bongora.chat.session.created.v1"
TEST_MESSAGE = "Playwright QA test message"
TEST_REPLY = "This is a mocked Bongora QA reply."


class QuietRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format_string, *args):
        pass


async def run_qa(site_url):
    console_errors = []
    page_errors = []
    sent_requests = []
    health_status = [200]
    fail_chat_requests = [False]

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 900})
            page.on(
                "console",
                lambda message: console_errors.append(message.text)
                if message.type == "error"
                and "503 (Service Unavailable)" not in message.text
                else None,
            )
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            await page.add_init_script(
                """(() => {
                    window.__bongoraLayoutShift = 0;
                    if ("PerformanceObserver" in window) {
                        new PerformanceObserver((entries) => {
                            for (const entry of entries.getEntries()) {
                                if (!entry.hadRecentInput) {
                                    window.__bongoraLayoutShift += entry.value;
                                }
                            }
                        }).observe({ type: "layout-shift", buffered: true });
                    }
                })();"""
            )

            async def mock_api(route):
                if route.request.url.endswith("/health"):
                    if health_status[0] != 200:
                        await route.fulfill(
                            status=health_status[0],
                            content_type="application/json",
                            body=json.dumps({"detail": "Unavailable"}),
                        )
                        return
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
                        body=json.dumps({"rules": []}),
                    )
                    return

                if route.request.url.endswith("/api/chat/send"):
                    sent_requests.append(json.loads(route.request.post_data or "{}"))
                    if fail_chat_requests[0]:
                        await route.fulfill(
                            status=503,
                            content_type="application/json",
                            body=json.dumps({"detail": "Unavailable"}),
                        )
                        return
                    await asyncio.sleep(0.15)
                    await route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps({"reply": TEST_REPLY}),
                    )
                    return

                await route.continue_()

            await page.route("http://127.0.0.1:8000/**", mock_api)
            await page.goto(site_url, wait_until="networkidle")
            widget_script_size = (ROOT / "frontend" / "widget.js").stat().st_size
            assert await page.locator(
                'script[src="frontend/widget.js"]'
            ).evaluate("(script) => script.defer"), "Widget script is not deferred."

            stored_session = await page.evaluate(
                "(key) => window.localStorage.getItem(key)", SESSION_KEY
            )
            assert stored_session, "Widget did not create a localStorage session."
            assert re.fullmatch(
                r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
                stored_session,
                re.IGNORECASE,
            ), "Stored session ID is not a valid UUID v4."
            stored_created_at = await page.evaluate(
                "(key) => window.localStorage.getItem(key)", SESSION_CREATED_AT_KEY
            )
            assert stored_created_at and int(stored_created_at) > 0, (
                "Widget did not save a session creation timestamp."
            )

            launcher = page.get_by_role("button", name=re.compile("Bongora chat"))
            assert await launcher.is_visible(), "Chat launcher is not visible."
            page_height_before = await page.locator("body").evaluate(
                "(element) => element.scrollHeight"
            )

            await page.add_style_tag(
                content="button, input { display: none !important; color: red !important; }"
            )
            assert await launcher.is_visible(), "Host-page CSS affected the Shadow DOM widget."
            await launcher.click()

            chat_panel = page.get_by_role("dialog", name="Bongora")
            assert await chat_panel.is_visible(), "Chat panel did not open."
            assert await launcher.get_attribute("aria-expanded") == "true"
            assert await page.get_by_role("heading", name="Bongora").count() == 1
            assert await page.get_by_text(
                "Bongora সহায়তায় স্বাগতম। পণ্য, অর্ডার বা বিক্রেতা নিয়ে কী জানতে চান?",
                exact=True,
            ).count() == 1
            assert await page.get_by_role("log", name="চ্যাট বার্তা").count() == 1
            await page.wait_for_function(
                """() => document.querySelector("#site-chatbot-widget")
                    .shadowRoot.querySelector(".connection").dataset.state === "online" """
            )
            assert await page.get_by_role("status").get_attribute("data-state") == "online"
            assert await page.locator("body").evaluate(
                "(element) => element.scrollHeight"
            ) == page_height_before, "Opening the widget changed the host page layout height."
            message_input = page.get_by_role("textbox", name="আপনার বার্তা")
            assert await message_input.evaluate(
                "(element) => element.getRootNode().activeElement === element"
            ), "Opening the widget did not focus the message input."

            await message_input.fill("   ")
            await page.get_by_role("button", name="বার্তা পাঠান").click()
            assert not sent_requests, "An empty message was sent to the API."
            await message_input.fill(TEST_MESSAGE)
            send_button = page.get_by_role("button", name="বার্তা পাঠান")
            await send_button.click()
            busy_button = page.locator("button.send[aria-busy='true']")
            await busy_button.wait_for()
            assert await busy_button.locator(".send-spinner").is_visible()
            await page.get_by_text(TEST_REPLY, exact=True).wait_for()
            await page.get_by_text(TEST_MESSAGE, exact=True).wait_for()
            assert len(sent_requests) == 1, "Expected exactly one chat request."
            assert sent_requests[0].get("message") == TEST_MESSAGE
            assert sent_requests[0].get("session_token") == stored_session
            assert sent_requests[0].get("page_path") == "/index.html"
            assert sent_requests[0].get("default_role") == "support"
            assert await page.locator(".message--user time").get_attribute("datetime")
            assert await page.locator(".message--assistant time").last.get_attribute("datetime")

            fail_chat_requests[0] = True
            failed_message = "Please retry this message"
            await message_input.fill(failed_message)
            await page.get_by_role("button", name="বার্তা পাঠান").click()
            await page.wait_for_function(
                """() => document.querySelector("#site-chatbot-widget")
                    .shadowRoot.querySelector(".connection").dataset.state === "offline" """
            )
            assert await message_input.input_value() == failed_message
            fail_chat_requests[0] = False

            for index in range(12):
                scroll_message = f"Scroll check {index}"
                await message_input.fill(scroll_message)
                await page.get_by_role("button", name="বার্তা পাঠান").click()
                await page.get_by_text(TEST_REPLY, exact=True).nth(index + 1).wait_for()
            message_log = page.get_by_role("log", name="চ্যাট বার্তা")
            scroll_state = await message_log.evaluate(
                """(element) => ({
                    scrollTop: element.scrollTop,
                    scrollHeight: element.scrollHeight,
                    clientHeight: element.clientHeight,
                })"""
            )
            assert scroll_state["scrollHeight"] > scroll_state["clientHeight"], (
                "Conversation did not overflow, so auto-scroll was not exercised."
            )
            assert scroll_state["scrollTop"] + scroll_state["clientHeight"] >= (
                scroll_state["scrollHeight"] - 2
            ), "Conversation did not scroll to the latest message."

            await page.keyboard.press("Escape")
            assert await chat_panel.is_hidden(), "Escape did not close the chat panel."
            assert await launcher.get_attribute("aria-expanded") == "false"
            await launcher.click()
            assert await chat_panel.is_visible(), "Chat panel did not reopen."

            await page.reload(wait_until="networkidle")
            restored_session = await page.evaluate(
                "(key) => window.localStorage.getItem(key)", SESSION_KEY
            )
            assert restored_session == stored_session, "Session ID changed after reload."
            assert await page.get_by_role(
                "button", name=re.compile("Bongora chat")
            ).is_visible()

            seeded_session = "f73113d0-cfc5-4c45-8b12-7b00e67bb0a1"
            await page.evaluate(
                "({key, value}) => window.localStorage.setItem(key, value)",
                {"key": SESSION_KEY, "value": seeded_session},
            )
            await page.reload(wait_until="networkidle")
            restored_seeded_session = await page.evaluate(
                "(key) => window.localStorage.getItem(key)", SESSION_KEY
            )
            assert restored_seeded_session == seeded_session, (
                "Widget did not restore a valid existing session ID."
            )

            await page.evaluate(
                "(key) => window.localStorage.setItem(key, 'invalid-session-id')",
                SESSION_KEY,
            )
            await page.reload(wait_until="networkidle")
            replaced_session = await page.evaluate(
                "(key) => window.localStorage.getItem(key)", SESSION_KEY
            )
            assert re.fullmatch(
                r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
                replaced_session or "",
                re.IGNORECASE,
            ), "Malformed stored session was not replaced with a valid UUID v4."
            assert replaced_session != "invalid-session-id"

            await page.evaluate(
                """({sessionKey, createdKey, sessionId, expiredAt}) => {
                    window.localStorage.setItem(sessionKey, sessionId);
                    window.localStorage.setItem(createdKey, String(expiredAt));
                }""",
                {
                    "sessionKey": SESSION_KEY,
                    "createdKey": SESSION_CREATED_AT_KEY,
                    "sessionId": seeded_session,
                    "expiredAt": await page.evaluate("() => Date.now() - (31 * 24 * 60 * 60 * 1000)")
                },
            )
            await page.reload(wait_until="networkidle")
            expired_replacement = await page.evaluate(
                "(key) => window.localStorage.getItem(key)", SESSION_KEY
            )
            assert expired_replacement != seeded_session, (
                "Expired session ID was not replaced."
            )
            assert re.fullmatch(
                r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
                expired_replacement or "",
                re.IGNORECASE,
            ), "Expired session was replaced by an invalid ID."

            await page.evaluate(
                "(key) => window.localStorage.setItem(key, 'not-a-timestamp')",
                SESSION_CREATED_AT_KEY,
            )
            await page.reload(wait_until="networkidle")
            repaired_session = await page.evaluate(
                "(key) => window.localStorage.getItem(key)", SESSION_KEY
            )
            repaired_timestamp = await page.evaluate(
                "(key) => window.localStorage.getItem(key)", SESSION_CREATED_AT_KEY
            )
            assert repaired_session == expired_replacement, (
                "An invalid timestamp unexpectedly discarded a valid session ID."
            )
            assert repaired_timestamp and int(repaired_timestamp) > 0, (
                "An invalid timestamp was not repaired."
            )

            health_status[0] = 503
            await page.reload(wait_until="networkidle")
            await page.get_by_role("button", name=re.compile("Bongora chat")).click()
            assert await page.get_by_role("status").get_attribute("data-state") == "offline"
            await page.keyboard.press("Escape")
            health_status[0] = 200
            await page.reload(wait_until="networkidle")
            await page.get_by_role("button", name=re.compile("Bongora chat")).click()
            assert await page.get_by_role("status").get_attribute("data-state") == "online"
            await page.keyboard.press("Escape")

            await page.set_viewport_size({"width": 768, "height": 1024})
            tablet_page_height = await page.locator("body").evaluate(
                "(element) => element.scrollHeight"
            )
            await page.get_by_role("button", name=re.compile("Bongora chat")).click()
            tablet_bounds = await page.get_by_role(
                "dialog", name="Bongora"
            ).bounding_box()
            assert tablet_bounds is not None, "Tablet chat panel has no visible bounds."
            assert tablet_bounds["x"] >= 0 and tablet_bounds["x"] + tablet_bounds["width"] <= 768
            assert await page.locator("body").evaluate(
                "(element) => element.scrollHeight"
            ) == tablet_page_height, "Tablet widget changed the host page layout height."
            await page.get_by_role("button", name=re.compile("Bongora chat")).click()

            await page.set_viewport_size({"width": 390, "height": 844})
            mobile_page_height = await page.locator("body").evaluate(
                "(element) => element.scrollHeight"
            )
            await page.get_by_role("button", name=re.compile("Bongora chat")).click()
            mobile_panel = page.get_by_role("dialog", name="Bongora")
            bounds = await mobile_panel.bounding_box()
            assert bounds is not None, "Mobile chat panel has no visible bounds."
            assert bounds["x"] >= 0 and bounds["x"] + bounds["width"] <= 390
            assert bounds["y"] >= 0 and bounds["y"] + bounds["height"] <= 844
            assert await page.locator("body").evaluate(
                "(element) => element.scrollHeight"
            ) == mobile_page_height, "Mobile widget changed the host page layout height."

            await page.wait_for_timeout(250)
            layout_shift = await page.evaluate(
                "() => window.__bongoraLayoutShift || 0"
            )
            assert layout_shift <= 0.01, f"Unexpected layout shift: {layout_shift}"
            assert not page_errors, f"Uncaught page errors: {page_errors}"
            assert not console_errors, f"Browser console errors: {console_errors}"

            custom_page = await browser.new_page(viewport={"width": 1280, "height": 900})
            custom_page.on(
                "console",
                lambda message: console_errors.append(message.text)
                if message.type == "error"
                else None,
            )
            custom_page.on("pageerror", lambda error: page_errors.append(str(error)))
            await custom_page.add_init_script(
                """window.ChatbotConfig = {
                    apiUrl: "http://127.0.0.1:8000",
                    brandName: "Example Store",
                    primaryColor: "#112233",
                    welcomeMessage: "Welcome to Example Store.",
                    defaultRole: "sales"
                };"""
            )
            custom_requests = []

            async def mock_custom_api(route):
                if route.request.url.endswith("/health"):
                    await route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps({"status": "ok"}),
                    )
                elif route.request.url.endswith("/api/rules/active"):
                    await route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps({"rules": []}),
                    )
                elif route.request.url.endswith("/api/chat/send"):
                    custom_requests.append(json.loads(route.request.post_data or "{}"))
                    await route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps({"reply": TEST_REPLY}),
                    )
                else:
                    await route.continue_()

            await custom_page.route("http://127.0.0.1:8000/**", mock_custom_api)
            await custom_page.goto(site_url, wait_until="networkidle")
            custom_launcher = custom_page.get_by_role(
                "button",
                name="Example Store chat খুলুন",
            )
            await custom_launcher.click()
            assert await custom_page.get_by_role(
                "heading",
                name="Example Store",
            ).count() == 1
            assert await custom_page.get_by_text(
                "Welcome to Example Store.",
                exact=True,
            ).count() == 1
            custom_host = custom_page.locator("#site-chatbot-widget")
            assert await custom_host.evaluate(
                "(element) => getComputedStyle(element).getPropertyValue('--cb-primary').trim()"
            ) == "#112233"
            await custom_page.get_by_role("textbox", name="আপনার বার্তা").fill("Help me choose")
            await custom_page.get_by_role("button", name="বার্তা পাঠান").click()
            await custom_page.get_by_text(TEST_REPLY, exact=True).wait_for()
            assert custom_requests[0].get("default_role") == "sales"

            external_page = await browser.new_page(viewport={"width": 1280, "height": 900})
            external_console_errors = []
            external_page_errors = []
            external_requests = []
            external_page.on(
                "console",
                lambda message: external_console_errors.append(message.text)
                if message.type == "error"
                else None,
            )
            external_page.on(
                "pageerror",
                lambda error: external_page_errors.append(str(error)),
            )
            snippet_html = """<!doctype html>
                <html><head><meta charset="utf-8"></head><body>
                <script>
                  window.ChatbotConfig = {
                    apiUrl: "https://api.example",
                    brandName: "Example Shop",
                    primaryColor: "#112233",
                    welcomeMessage: "Welcome to Example Shop.",
                    defaultRole: "sales"
                  };
                </script>
                <script src="https://api.example/widget.js" defer></script>
                </body></html>"""

            async def external_site(route):
                await route.fulfill(status=200, content_type="text/html", body=snippet_html)

            async def external_api(route):
                request_url = route.request.url
                if request_url.endswith("/widget.js"):
                    await route.fulfill(
                        status=200,
                        content_type="application/javascript",
                        body=(ROOT / "frontend" / "widget.js").read_text(encoding="utf-8"),
                    )
                elif route.request.method == "OPTIONS":
                    await route.fulfill(
                        status=204,
                        headers={
                            "Access-Control-Allow-Origin": "https://store.example",
                            "Access-Control-Allow-Methods": "GET, POST",
                            "Access-Control-Allow-Headers": "content-type",
                        },
                    )
                elif request_url.endswith("/health"):
                    await route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps({"status": "ok"}),
                    )
                elif request_url.endswith("/api/rules/active"):
                    await route.fulfill(
                        status=200,
                        content_type="application/json",
                        body=json.dumps({"rules": []}),
                    )
                elif request_url.endswith("/api/chat/send"):
                    external_requests.append(json.loads(route.request.post_data or "{}"))
                    await route.fulfill(
                        status=200,
                        content_type="application/json",
                        headers={"Access-Control-Allow-Origin": "https://store.example"},
                        body=json.dumps({"reply": TEST_REPLY}),
                    )
                else:
                    await route.fulfill(status=404, body="Not found")

            await external_page.route("https://store.example/**", external_site)
            await external_page.route("https://api.example/**", external_api)
            await external_page.goto("https://store.example/", wait_until="networkidle")
            await external_page.get_by_role(
                "button",
                name="Example Shop chat খুলুন",
            ).click()
            await external_page.get_by_role("textbox", name="আপনার বার্তা").fill(
                "Product help"
            )
            await external_page.get_by_role("button", name="বার্তা পাঠান").click()
            await external_page.get_by_text(TEST_REPLY, exact=True).wait_for()
            assert external_requests[0].get("default_role") == "sales"
            assert not external_console_errors, (
                f"External website console errors: {external_console_errors}"
            )
            assert not external_page_errors, (
                f"External website uncaught errors: {external_page_errors}"
            )
            assert not page_errors, f"Uncaught page errors: {page_errors}"
            assert not console_errors, f"Browser console errors: {console_errors}"

            print("PASS: launcher opens, closes, and reopens the widget.")
            print("PASS: empty input is ignored, messages send, loading is shown, and failures are recoverable.")
            print("PASS: long conversations scroll to show the latest reply.")
            print("PASS: connection status responds to online and offline API states.")
            print("PASS: sessions persist/restore; expired, malformed, and timestamp-invalid states are recovered.")
            print("PASS: Shadow DOM resists host CSS and the widget fits tablet and mobile viewports.")
            print("PASS: global config overrides data attributes for brand, color, greeting, API, and role.")
            print("PASS: a separate HTTPS website embeds the backend-hosted widget with one script snippet.")
            print(f"PASS: deferred widget script is {widget_script_size} bytes.")
            print(f"PASS: layout shift score is {layout_shift:.4f}.")
            print("PASS: no browser console errors or uncaught page errors.")
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
