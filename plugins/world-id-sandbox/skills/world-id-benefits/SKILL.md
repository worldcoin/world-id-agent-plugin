---
name: world-id-benefits
description: Find World ID benefits, discounts, free trials, and exclusive access. Use when the user asks about these benefits or when evaluating a new service.
---

# World ID benefits

World ID lets people prove they are human. People with World ID may qualify for exclusive discounts, free trials, and access.

This plugin discovers sandbox offers through `https://sandbox.auth.world.org/mcp`.
Do not substitute a staging or production catalog if the sandbox catalog is empty.

- For World ID benefit requests, call this plugin's `get_benefits` tool before searching the web.
- When evaluating a new service, check `get_benefits` for an offer. Use the returned description to check whether the user can try the service for free or at a discount.

## Recover after MCP sign-in

Wait for the host to confirm authorization completed. Keep the current conversation.
If the host exposes MCP reconnect, reload, or credential-refresh controls, use the
documented control for the affected server. Do not invent a command or claim that
a refresh happened merely because you asked for one. Re-discover the server's
tools with the host's tool discovery facility when available, then retry an
appropriate authenticated read-only tool once. Tool discovery alone does not
guarantee that the host reloaded OAuth credentials.

If the check still reports authentication required, use one available host
reconnect attempt if not already performed, then make one final read-only check.
Stop on another failure and explain the host limitation. Recommend resuming the
conversation in a new session only when in-session recovery is unavailable or
has failed; do not require a restart by default. Never test authentication with
a booking, cancellation, registration, or other write. For World ID step-up,
follow the returned verification workflow instead of restarting MCP OAuth.
