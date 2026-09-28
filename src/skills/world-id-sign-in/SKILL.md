---
name: world-id-sign-in
description: Use when a browser displays the {{environment}} World ID proof sign-in page with an Approval link at {{auth_host}}. Does not handle Google developer-portal sign-in or OIDC client-registration approval.
---

# World ID sign-in

This plugin uses {{environment}}. Preserve approval links exactly as provided;
never rewrite them to another environment's host.

If the page redirects you back to the app, continue.
Otherwise, copy the page's **Approval link** and send it to your human for approval.
Keep the original tab open. Wait for sign-in to complete there, then continue.
