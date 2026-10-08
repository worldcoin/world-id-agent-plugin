---
name: world-id-sign-in
description: Use when a browser displays the sandbox World ID proof sign-in page with an Approval link at sandbox.auth.world.org. Does not handle Google developer-portal sign-in or OIDC client-registration approval.
---

# World ID sign-in

This plugin uses sandbox. Preserve approval links exactly as provided;
never rewrite them to another environment's host.

For any browser or computer-use steps, use the user's default system browser
with their existing profile, the same browser used for plugin authorization,
so existing signed-in sessions can be reused. Identify it from available system
or browser information; if unclear, ask the user which browser they use.
Do not use the built-in OpenAI browser. If the default browser cannot be
controlled or access is declined, provide the link and steps for the user to
complete there instead. If sign-in started in the built-in browser, restart
sign-in from the service in the default system browser before proceeding.

If the page redirects you back to the app, continue.
Otherwise, copy the page's **Approval link** and send it to your human for approval.
Keep the original tab open. Wait for sign-in to complete there, then continue.
