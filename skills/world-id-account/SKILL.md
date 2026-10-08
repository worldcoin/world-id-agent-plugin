---
name: world-id-account
description: Connect the user's World ID or check its connection status. Use for World ID sign-in, account, identifier, or verification-status requests.
---

# World ID Account

This plugin uses the sandbox environment at `https://sandbox.auth.world.org/mcp`.
Use only its bundled MCP connection; never switch environments.

For any browser or computer-use steps, use the user's default system browser
with their existing profile, the same browser used for plugin authorization,
so existing signed-in sessions can be reused. Identify it from available system
or browser information; if unclear, ask the user which browser they use.
Do not use the built-in OpenAI browser. If the default browser cannot be
controlled or access is declined, provide the link and steps for the user to
complete there instead.

When reporting account details, disclose only connection status. Never disclose
`continuity_handle` or other personal identifiers, including partial or transformed
values, or quote raw tool responses or errors.

For a connection request, explain that the user will sign in with World ID in
their default system browser, then start the host's MCP authorization flow if
not already connected.
Request `world-id:read`, preserving any previously granted scopes. In Codex, when
native connection controls are unavailable, run
`codex mcp login world-id-sandbox --scopes world-id:read` (include existing scopes
if known). Share the command's authorization URL if the browser does not open.
In Claude Code, use the matching server's authentication flow in `/mcp`.

For a status check, or after successful authorization, call `get_world_id_account`
with no arguments. If the first check after successful Codex CLI login still
requires authentication, the session may have stale credentials: ask the user to
check again in a completely new Codex chat, then stop. Do not repeat login or
report that authorization failed solely because this session remains unauthenticated.
Report connected only for an error-free response containing
`status: active` and `world_id_verified: true`; otherwise report not connected
when both status fields are valid. If authorization is required,
explain that sign-in is needed and offer to connect; continue if already requested.
If login is declined or fails, stop and summarize the cause. Do not retry in a loop.
For other tool failures or invalid status fields, report that status could not
be determined. Never ask for credentials, proofs, tokens, or identifiers in chat.
