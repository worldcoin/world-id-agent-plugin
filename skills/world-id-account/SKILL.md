---
name: world-id-account
description: Connect the user's World ID or check its connection status. Use for World ID sign-in, account, identifier, or verification-status requests.
---

# World ID Account

This plugin uses the sandbox environment at `https://sandbox.auth.world.org/mcp`.
Use only its bundled MCP connection; never switch environments.

For browser tasks, open links in the user's default system browser and use
computer use to continue in that browser's existing profile. Reuse any tab
already opened by plugin authentication. Do not use the built-in OpenAI browser.
If you cannot control the user's browser, provide the link and instructions for
them to finish.

When reporting account details, disclose only connection status. Never disclose
`continuity_handle` or other personal identifiers, including partial or transformed
values, or quote raw tool responses or errors.

For a status check or connection request, call `get_world_id_account` with no
arguments. Its authentication challenge lets the host present sign-in. If the
tool is unavailable, use the installed plugin's connection controls.

When connection is requested, use the active host's MCP authorization flow,
requesting `world-id:read` and preserving previously granted scopes:

- In ChatGPT/Codex desktop or a workspace-directory installation, use the native
  **Connect** or **Reconnect** control. If no tool can activate it, direct the
  user to the World ID reconnect banner or the plugin's connection settings.
  Explain that clicking it opens browser sign-in; do not claim to have opened it.
  Do not run `codex mcp login` as a fallback for these installations: the desktop
  can load the plugin's tools even when the standalone CLI cannot find its server.
- For a Codex CLI session, first confirm `codex mcp list` includes
  `world-id-sandbox` at this plugin's endpoint in the same execution environment.
  Then run `codex mcp login world-id-sandbox --scopes world-id:read`, including
  existing scopes if known. Share the command's authorization URL if the browser
  does not open. If the server is missing, explain the configuration issue rather
  than attempting login or creating a second connection.
- In Claude Code, use the matching server's authentication flow in `/mcp`.

Cancellation leaves sign-in incomplete. Stop the current attempt, but if the
user later asks to connect, follow this flow again. The host may label an initial
or cancelled sign-in **Reconnect** or **Authentication expired**; that wording
alone does not establish that a previously connected account expired.

After authorization completes, check `get_world_id_account` again in the same
chat. If the tool remains unavailable or requires authentication, report that
this chat cannot yet confirm the connection and use the host's available
connection status or refresh controls. Suggest a new chat only as a recovery
step if those controls do not resolve it; do not automatically repeat login or
conclude that World ID verification failed.
Report connected only for an error-free response containing
`status: active` and `world_id_verified: true`; otherwise report not connected
when both status fields are valid. If authorization is required,
explain that sign-in is needed and offer to connect; continue if already requested.
If login is declined or fails, stop and summarize the cause. Do not retry in a loop.
For other tool failures or invalid status fields, report that status could not
be determined. Never ask for credentials, proofs, tokens, or identifiers in chat.
