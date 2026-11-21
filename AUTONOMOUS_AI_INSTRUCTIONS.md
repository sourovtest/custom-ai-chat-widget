# Bongora — Autonomous AI Customer Support & Sales Chatbot

## Project Objective

Build a lightweight, secure, production-ready, embeddable chatbot for the Bongora multivendor e-commerce website. It should provide natural customer conversations in Bengali, Banglish, and English; understand intent and context; assist with product discovery, sales, support, and FAQs; route conversations by page and intent; support administrator-managed behavior; and preserve sessions across reloads without negatively affecting the host website.

Never fabricate product prices, stock, delivery times, policies, or order information. When verified information is unavailable, state the limitation and offer an appropriate support path.

## Technology and Architecture

- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Shadow DOM, and `localStorage`.
- **Backend:** Python, FastAPI, REST, and JSON.
- **Database:** MySQL with relational integrity and appropriate indexes.
- **AI:** Configurable Gemini and/or OpenAI provider, environment-based credentials, context-aware prompts, and usage monitoring.
- Use a modular, maintainable architecture, secure API communication, and no unnecessary frameworks or dependencies.

Expected project structure:

```text
BONGORA-AI-CHATBOT/
├── database/schema.sql
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── ...
├── frontend/widget.js
├── admin/index.html
├── tests/
├── index.html
├── AUTONOMOUS_AI_INSTRUCTIONS.md
├── PROJECT_PROGRESS.md
├── INTEGRATION_GUIDE.md
└── README.md
```

Additional folders may be introduced only when technically necessary and documented. Inspect before creating files; avoid duplicates and preserve existing behavior. Never overwrite working code without reading it.

## AI Development Team Roles

1. **Overall Supervisor (Tech Lead):** Plans one task at a time, maintains architecture, approves milestones, synchronizes documentation, and updates `PROJECT_PROGRESS.md`.
2. **Frontend Developer:** Builds `frontend/widget.js` and `admin/index.html`, ensures isolated CSS, bespoke responsive UI, accessibility, and `localStorage` session persistence.
3. **Backend Developer:** Builds `database/schema.sql` and FastAPI endpoints in `backend/main.py`; configures secure CORS, database access, last-five-message context, and LLM integration.
4. **QA Engineer:** Reviews every changed file for correctness, security, XSS/SQL injection, CORS, broken flows, console errors, and natural chatbot responses. Do not mark work complete until applicable QA checks pass.

## Chatbot Personas and Routing

### Base Persona

Respond as an empathetic, real Bongora support executive for buyers and sellers. Keep replies short and conversational, like live chat. Never use robotic phrases such as “As an AI...” or “Certainly!”. Reply naturally in Bengali or Banglish when the user does.

### Dynamic Roles

- `/product` and `/cart` → Sales Assistant.
- `/contact` and `/tracking` → Customer Support.
- `/dashboard` → Vendor Assistant.
- `/faq` → FAQ Assistant.
- `?test_mode=true` → Internal QA Assistant; never expose internal QA behavior to regular customers.

Match URLs carefully, including query parameters. Keep routing configurable and consider customer context and intent.

## Quality, SEO, Accessibility, and Human-Crafted Standards

These are mandatory for every agent and every change:

1. **Bespoke Design:** Never use generic AI UI templates, cliché purple/blue gradients, generic SaaS layouts, or robotic boilerplate styling. Create a clean, custom Bongora-specific design with subtle micro-interactions, natural spacing, and realistic typography.
2. **Human-Written Code:** Write clean, idiomatic, production-grade code. Avoid robotic comments, unnecessary boilerplate, and dead code.
3. **SEO and Core Web Vitals:** Keep `widget.js` ultra-lightweight, load the integration script asynchronously with `defer`, and cause zero Cumulative Layout Shift. Use Shadow DOM or strict CSS prefixing to avoid host-site conflicts. Use semantic, accessible HTML in the widget and Admin Panel, including suitable `aria-label`, button, and role attributes.
4. **Production Readiness:** Handle API timeouts, offline state, empty input, and network errors gracefully. Sanitize/validate user input against XSS and use parameterized SQL queries against SQL injection. QA must verify zero console errors and zero broken flows in changed functionality before marking work complete.

## Security and Data Protection

1. Prevent SQL injection with parameterized queries; validate and sanitize all user input and prevent XSS.
2. Apply appropriate CSRF protections, API rate limits, secure administrator authentication, and role-based authorization.
3. Protect credentials with environment variables; never expose secrets or store passwords in plaintext.
4. Restrict CORS to approved origins. Never expose internal error details or unnecessary personal information.
5. Protect customer data; define retention and deletion policies.
6. Defend against prompt injection. Never treat user input as system instructions.
7. Require relevant security tests before claiming the system is secure.

## Development and Approval Rules

- Read `PROJECT_PROGRESS.md` first at the start of every session.
- Inspect the existing project and relevant files before acting.
- Work on one authorized task at a time; do not skip phases.
- Never start a development phase without explicit user authorization. Never begin a later phase until the current phase passes QA and receives user approval.
- Ask before destructive operations, database resets, destructive migrations, production integration, or deployment.
- Stay within approved scope. Fix safe, identifiable errors; retry failed tests when appropriate; report unresolved issues honestly.
- For each authorized task: analyze, plan, implement, test, resolve errors, verify actual results, update documentation, and report.
- At phase completion, provide a QA report with completed tasks, tests passed/failed, bugs found/fixed, limitations, and security observations. Update documentation and wait for explicit user approval before the next phase.
- Do not claim tests, security, or progress that have not been verified. Only verified completed checklist items count toward progress.

## Autonomous Problem-Solving Rule

If any tool call, preview, or command fails twice, never get stuck in a retry loop. Immediately diagnose why it failed, find a working alternative (for example, install a missing package, use terminal-based Playwright or CLI tools, or write a test script), solve the blocker yourself, and continue the workflow seamlessly.

## Official Five-Phase Roadmap

At initialization, all tasks start pending. Use `[ ]` Pending, `[~]` In Progress, `[x]` Completed and verified, and `[!]` Blocked. Do not change a task to `[x]` without applicable QA evidence and authorization. Keep this checklist synchronized with `PROJECT_PROGRESS.md`.

### Phase 1: Project Setup & Database Foundation — Completed

#### 1.1 Project Structure

- [x] Create clean folder structure: `database/`, `backend/`, `frontend/`, `admin/`, `tests/`.
- [x] Create and organize required project documentation.
- [x] Verify the directory structure.

#### 1.2 Database Architecture

- [x] Create `database/schema.sql`.
- [x] Design optimized MySQL database architecture.
- [x] Create `chat_sessions` table.
- [x] Create `chat_messages` table.
- [x] Create `chatbot_rules` table.
- [x] Add appropriate primary keys and foreign keys.
- [x] Add optimized indexes.
- [x] Define timestamps and database constraints.
- [x] Prepare a safe database migration strategy.

#### 1.3 Backend Foundation

- [x] Create `backend/requirements.txt`.
- [x] Create `backend/.env.example`.
- [x] Create `backend/main.py`.
- [x] Configure FastAPI application.
- [x] Configure secure CORS settings.
- [x] Implement `GET /health`.
- [x] Establish database connection architecture.
- [x] Configure environment-based settings.

#### 1.4 Frontend Placeholders

- [x] Create `frontend/widget.js` placeholder.
- [x] Create `admin/index.html` placeholder.
- [x] Create root `index.html` for local testing.

#### 1.5 Phase 1 QA

- [x] Verify folder structure.
- [x] Verify Python syntax.
- [x] Verify dependencies.
- [x] Verify database schema syntax against MySQL 8.0.
- [x] Verify database connection configuration.
- [x] Confirm zero hardcoded secrets.
- [x] Generate Phase 1 QA report.

### Phase 2: Frontend Chat Widget — Completed

#### 2.1 Custom UI Design

- [x] Design a bespoke, human-crafted chatbot for Bongora.
- [x] Avoid generic AI chatbot templates.
- [x] Design a modern floating action button (FAB).
- [x] Build the expandable chat window.
- [x] Add chatbot avatar and name.
- [x] Add online/offline status indicator.
- [x] Create a scrollable conversation area.
- [x] Create a message input field.
- [x] Add send button and loading indicator.
- [x] Design customer and bot message bubbles.
- [x] Add appropriate timestamps.
- [x] Add error and offline states.

#### 2.2 Frontend Architecture

- [x] Implement Shadow DOM or equivalent strict CSS isolation.
- [x] Prevent conflicts with Bongora website CSS.
- [x] Use semantic and accessible HTML.
- [x] Implement keyboard accessibility.
- [x] Support mobile, tablet, and desktop.
- [x] Ensure zero layout shifts (CLS).
- [x] Load scripts asynchronously or with `defer` where appropriate.
- [x] Avoid unnecessary external dependencies.
- [x] Keep widget assets lightweight.

#### 2.3 Session Management

- [x] Generate unique `session_id`.
- [x] Save `session_id` in `localStorage`.
- [x] Restore existing sessions.
- [x] Maintain session across page reloads.
- [x] Handle expired or invalid sessions safely.

#### 2.4 Local Testing

- [x] Connect `widget.js` to `index.html`.
- [x] Verify widget open/close behavior.
- [x] Verify message input behavior.
- [x] Verify scrolling behavior.
- [x] Verify responsive layout.

#### 2.5 Phase 2 QA

- [x] Verify zero CSS conflicts.
- [x] Verify no JavaScript console errors.
- [x] Verify responsive behavior.
- [x] Verify accessibility.
- [x] Verify session persistence.
- [x] Verify performance and CLS.
- [x] Generate Phase 2 QA report.

### Phase 3: Backend API & AI Brain — Completed

#### 3.1 API Development

- [x] Implement `POST /api/chat/send`.
- [x] Implement session creation endpoint.
- [x] Implement session history endpoint.
- [x] Implement message history retrieval.
- [x] Implement request validation.
- [x] Implement structured JSON responses.
- [x] Implement proper HTTP error handling.

#### 3.2 Database Integration

- [x] Connect FastAPI with MySQL.
- [x] Save incoming customer messages.
- [x] Retrieve the last 5 messages for conversational context.
- [x] Save AI-generated responses.
- [x] Maintain session-message relationships.
- [x] Use parameterized SQL queries.
- [x] Handle database failures gracefully.

#### 3.3 Human-like AI Brain

- [x] Develop the Human-like Base Prompt.
- [x] Implement Anti-AI robotic response rules.
- [x] Support natural Bengali conversations.
- [x] Support Banglish conversations.
- [x] Support English conversations.
- [x] Implement automatic language detection.
- [x] Implement context-aware responses.
- [x] Implement customer intent detection.
- [x] Implement sentiment-aware responses.
- [x] Implement product recommendation logic.
- [x] Implement sales objection handling.
- [x] Implement fallback responses.
- [x] Implement human-agent handoff logic.

#### 3.4 Dynamic Role Routing

- [x] Implement `/product` → Sales Assistant routing.
- [x] Implement `/cart` → Sales Assistant routing.
- [x] Implement `/contact` → Customer Support routing.
- [x] Implement `/tracking` → Customer Support routing.
- [x] Implement `/dashboard` → Vendor Assistant routing.
- [x] Implement `/faq` → FAQ Assistant routing.
- [x] Implement `?test_mode=true` → Internal QA Assistant routing.
- [x] Apply URL matching carefully.
- [x] Support query parameters.
- [x] Prevent incorrect role assignments.
- [x] Keep routing logic configurable.
- [x] Prevent exposure of internal QA behavior to normal customers.

#### 3.5 LLM Integration

- [x] Integrate Gemini API and/or OpenAI API.
- [x] Support configurable AI providers.
- [x] Secure API keys using environment variables.
- [x] Implement API timeout handling.
- [x] Implement retry and failure handling.
- [x] Implement token usage tracking.
- [x] Implement AI response validation.
- [x] Save bot responses to MySQL.
- [x] Return structured JSON to the frontend.

#### 3.6 Phase 3 QA

- [x] Verify all API endpoints.
- [x] Verify parameterized SQL queries.
- [x] Verify SQL injection protection.
- [x] Verify LLM integration.
- [x] Verify timeout and API error handling.
- [x] Verify conversation context.
- [x] Verify language detection.
- [x] Verify dynamic role routing.
- [x] Verify human-like response quality.
- [x] Generate Phase 3 QA report.

### Phase 4: Visual Admin Panel — Completed

#### 4.1 Admin Interface

- [x] Design a clean, modern custom Admin UI.
- [x] Build a dashboard overview.
- [x] Display chatbot rule statistics.
- [x] Build a chatbot rules management interface.
- [x] Add create, edit, activate, deactivate, and delete controls.

#### 4.2 Chatbot Rules Management

- [x] Support custom administrator-defined rule names.
- [x] Support `on_first_visit` trigger event.
- [x] Support `time_on_page` trigger event.
- [x] Support `url_match` trigger event.
- [x] Support Static Message action.
- [x] Support AI Persona action.
- [x] Support Sales Assistant role.
- [x] Support Customer Support role.
- [x] Support Vendor Assistant role.
- [x] Support FAQ Assistant role.
- [x] Support Custom AI Persona role.
- [x] Configure trigger conditions.
- [x] Configure trigger delay.
- [x] Configure priority.
- [x] Configure active/inactive status.
- [x] Configure rule execution frequency.
- [x] Prevent duplicate trigger execution.

#### 4.3 Backend CRUD API

- [x] Implement `GET /api/rules`.
- [x] Implement `POST /api/rules`.
- [x] Implement `PUT /api/rules/{id}`.
- [x] Implement `DELETE /api/rules/{id}`.
- [x] Implement rule validation.
- [x] Implement administrator authorization.
- [x] Implement database persistence.

#### 4.4 Frontend Rule Execution

- [x] Connect Admin UI to backend.
- [x] Load saved chatbot rules.
- [x] Update existing rules.
- [x] Delete rules safely.
- [x] Update `widget.js` to evaluate active trigger rules.
- [x] Execute static messages correctly.
- [x] Execute AI Persona actions correctly.
- [x] Prevent duplicate rule execution.
- [x] Handle rule conflicts and priorities.

#### 4.5 Phase 4 QA

- [x] Verify rule creation.
- [x] Verify rule editing.
- [x] Verify rule deletion.
- [x] Verify rule activation/deactivation.
- [x] Verify database persistence.
- [x] Verify trigger execution.
- [x] Verify administrator authorization.
- [x] Generate Phase 4 QA report.

### Phase 5: Final QA, Security Audit & Bongora Integration — In Progress

#### 5.1 End-to-End Testing

- [x] Test the complete customer conversation flow.
- [x] Test offline state.
- [x] Test empty inputs.
- [x] Test invalid inputs.
- [x] Test session persistence.
- [x] Test multiple customer sessions.
- [x] Test database failures.
- [x] Test LLM API failures.
- [x] Test responsive design.
- [x] Test role routing.
- [x] Test chatbot rules.
- [x] Test human-agent handoff.

#### 5.2 Security Audit

- [x] Test SQL injection protection.
- [x] Test XSS sanitization.
- [x] Test API input validation.
- [x] Verify CORS restrictions.
- [x] Verify admin authentication.
- [x] Verify authorization boundaries.
- [x] Verify secure environment variables.
- [x] Verify prompt injection defenses.
- [x] Verify sensitive data protection.
- [x] Verify rate limiting.
- [!] Verify HTTPS requirements.

#### 5.3 Performance Audit

- [x] Measure widget loading performance.
- [x] Verify zero unnecessary layout shifts.
- [x] Check JavaScript bundle size.
- [x] Optimize API response time.
- [x] Optimize database queries.
- [x] Check memory usage.
- [x] Verify no duplicate API requests.
- [x] Verify no memory leaks.
- [x] Confirm no significant negative impact on Bongora Core Web Vitals.

#### 5.4 Deployment & Recovery

- [x] Prepare production configuration.
- [x] Prepare production environment variables.
- [x] Document deployment steps.
- [x] Prepare database backup strategy.
- [x] Prepare database recovery strategy.
- [x] Document rollback procedures.
- [x] Configure production health checks.
- [x] Verify server restart recovery.

#### 5.5 Bongora Website Integration

- [x] Generate the final lightweight script integration snippet.
- [x] Create `INTEGRATION_GUIDE.md`.
- [x] Document the integration process.
- [x] Document configuration options.
- [x] Document troubleshooting.
- [!] Test integration on a staging website.
- [!] Verify no conflicts with the main Bongora website.
- [!] Obtain approval before production integration.

#### 5.6 Final Sign-off

- [x] Complete full regression testing.
- [x] Resolve all critical and high-priority bugs.
- [x] Document remaining known limitations.
- [x] Generate final security audit report.
- [x] Generate final QA report.
- [ ] Verify all approved requirements.
- [ ] Obtain final user approval.
- [ ] Update `PROJECT_PROGRESS.md` to 100%.

## Logging, Monitoring, and Performance

- Log backend errors, API requests, database failures, AI API failures, admin activity, and failed messages without recording passwords, API keys, or unnecessary personal information.
- Monitor API response time, AI latency, database health, failed request rate, token usage, and availability.
- Keep the frontend lightweight; optimize assets, queries, and API responses. Avoid unnecessary third-party dependencies, duplicate requests, and memory leaks. Minimize impact on the host site's Core Web Vitals.

## Documentation Policy

- `AUTONOMOUS_AI_INSTRUCTIONS.md`: objectives, architecture, standards, security, workflow, and roadmap.
- `PROJECT_PROGRESS.md`: synchronized five-phase checklist, verified progress, QA results, issues, blockers, and next authorized action.
- `README.md`: overview, stack, installation, configuration, development setup, and API overview.
- `INTEGRATION_GUIDE.md`: Bongora integration snippet, options, troubleshooting, and deployment notes.
- Update documentation when an authorized milestone is completed and verified.

## Progress and Phase Approval

- Overall Progress = verified completed tasks / total tasks × 100.
- In-progress and blocked tasks do not count as complete. Never inflate progress.
- At initialization, overall progress is 0% and all five phases are pending.
- For each phase: develop only authorized scope; test; resolve errors; prepare a QA report (completed work, tests passed/failed, bugs, limitations, security observations); update documentation; wait for explicit user approval. Only then may the next phase begin.
- Never skip a phase, fabricate test results, claim unverified security, or deploy without approval.

## Initialization Record

The original documentation-only initialization is complete. Phase 1 was subsequently authorized and is now completed and QA-verified. Follow the current phase status in `PROJECT_PROGRESS.md`; do not begin Phase 2 until the user explicitly approves the next phase.
