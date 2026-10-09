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

Call `get_world_id_account` with no arguments to check status or begin connecting.
If sign-in is required, offer to connect; proceed if already requested. Request
`world-id:read`, preserving existing scopes:

- **Desktop/workspace plugin:** use native **Connect/Reconnect**. If you cannot
  activate it, point to the reconnect banner or plugin connection settings.
  Use these controls if the account tool is unavailable too. Do not substitute
  CLI login or claim the browser opened before it does.
- **Codex CLI session:** run `codex mcp login world-id-sandbox --scopes world-id:read`
  only after `codex mcp list` confirms this server and endpoint in the same
  environment. Include existing scopes; share the authorization URL if needed.
  Report a missing server instead of creating a second connection.
- **Claude Code:** authenticate the matching server through `/mcp`.

After sign-in, check status again in the same chat. If still unauthenticated or
unavailable, report the connection as unconfirmed and try the host's status or
refresh controls before suggesting a new chat. This does not prove verification
failed. **Reconnect/Authentication expired** can also label an initial sign-in.

Report connected only for an error-free response with `status: active` and
`world_id_verified: true`; otherwise report not connected when both fields are
valid. Other errors or invalid fields mean status is unknown.

Stop and explain cancelled or failed sign-in; retry only when requested later.
Never ask for credentials, proofs, tokens, or identifiers in chat.
