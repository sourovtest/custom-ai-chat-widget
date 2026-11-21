# GitHub Copilot Instructions

At the start of every session, always read `AUTONOMOUS_AI_INSTRUCTIONS.md` and `PROJECT_PROGRESS.md`. Follow the defined development team roles and one-milestone-at-a-time execution protocol. After finishing any task, run the relevant QA checks and update `PROJECT_PROGRESS.md` before proceeding.

## Autonomous Problem-Solving Rule

If any tool call, preview, or command fails twice, never get stuck in a retry loop. Immediately diagnose why it failed, find a working alternative (for example, install a missing package, use terminal-based Playwright or CLI tools, or write a test script), solve the blocker yourself, and continue the workflow seamlessly.

## Quality, SEO & Human-Crafted Standards

These non-negotiable rules apply to every change:

1. **No Generic AI Templates (100% Bespoke Design):** Never use generic, overused AI UI templates, cliché purple/blue gradients, generic SaaS layouts, or robotic boilerplate styling. Create a clean, custom, human-crafted UI specifically tailored for Bongora with subtle micro-interactions, natural spacing, and realistic typography.
2. **Human-Written Code Quality (No AI-Looking Code):** Write clean, idiomatic, production-grade code like a senior human developer. Avoid robotic AI-style comments (such as `// Initialize variable`), unnecessary boilerplate, and dead code.
3. **SEO & Core Web Vitals Friendly:** Keep `frontend/widget.js` ultra-lightweight and load it asynchronously with `defer` in the host integration script. The widget must cause zero Cumulative Layout Shift (CLS). Use Shadow DOM or strict CSS prefixing to avoid host-site style conflicts. Use clean, semantic, accessible HTML for the widget and Admin Panel, including appropriate `aria-label` values and button/role attributes.
4. **Zero-Bug & Production-Ready Policy:** Handle API timeouts, offline state, empty inputs, and network errors gracefully. Sanitize user input against XSS and use parameterized queries against SQL injection. QA must verify zero console errors and zero broken flows for changed functionality before updating `PROJECT_PROGRESS.md` to mark the task complete.
