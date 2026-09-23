---
name: world-id-account
description: Check the user's connected World ID account. Use when the user asks "what's my World ID?", requests their World ID identifier or continuity handle, or wants to check their World ID connection or verification status.
---

# World ID Account

This plugin uses the sandbox environment at `https://sandbox.auth.world.org/mcp`.
Use its bundled MCP connection, not a staging or production World ID connection.
MCP authentication is a setup prerequisite, handled outside this skill.

1. Call `get_world_id_account` from this plugin's World ID MCP server with no arguments.
2. If authorization is required, report that the MCP connection is not authorized,
   refer the user to the README's setup instructions, and stop. Do not initiate
   login or repeatedly retry the tool.
3. Report a connected account
   only when it returns `status: active` and `world_id_verified: true` without an error.
   When the user asks for their World ID, return `continuity_handle` and describe it as
   their sector-specific continuity handle, not a global or internal account ID. This
   confirms prior verification, not fresh human presence or that the agent is human.
4. If the tool fails, explain the error briefly; do not report a connected account.
   Never ask for credentials, proofs, tokens, or account identifiers in chat.

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
