---
name: world-id-sign-in
description: Use when a browser displays the production World ID proof sign-in page with an Approval link at auth.world.org. Does not handle Google developer-portal sign-in or OIDC client-registration approval.
---

# World ID sign-in

This plugin uses production. Preserve approval links exactly as provided;
never rewrite them to another environment's host.

For browser tasks, open links in the user's default system browser and use
computer use to continue in that browser's existing profile. Reuse any tab
already opened by plugin authentication. Do not use the built-in OpenAI browser.
If you cannot control the user's browser, provide the link and instructions for
them to finish.

If the page redirects you back to the app, continue.
Otherwise, copy the page's **Approval link** and send it to your human for approval.
Keep the original tab open. Wait for sign-in to complete there, then continue.
