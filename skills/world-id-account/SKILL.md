---
name: world-id-account
description: Report only whether the user's World ID account is connected. Use when the user asks about their World ID account, identifier, continuity handle, connection, or verification status.
---

# World ID Account

This plugin uses the production environment at `https://auth.worldcoin.dev/mcp`.
Use only its bundled MCP connection; never switch environments.
MCP authentication is a setup prerequisite, handled outside this skill.

Only report connection status to the user, even when they explicitly request an
identifier or account details. Never disclose `continuity_handle` or any other
personal account identifier, including partial or transformed values. Do not
quote raw tool responses or errors, which may contain identifiers.

1. Call `get_world_id_account` from this plugin's World ID MCP server with no arguments.
2. If authorization is required, report that the MCP connection is not authorized,
   refer the user to the README's setup instructions, and stop. Do not initiate
   login or repeatedly retry the tool.
3. For a successful, complete response, say "Your World ID account is connected."
   only when it returns `status: active` and `world_id_verified: true` without an error.
   Otherwise, say "Your World ID account is not connected."
4. If the tool fails or the status fields are missing or invalid, say that you
   couldn't determine whether the account is connected. Briefly summarize any
   actionable cause without including account identifiers or raw error details.
   Never ask for credentials, proofs, tokens, or account identifiers in chat.
