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
