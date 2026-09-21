---
name: world-id-account
description: Get, connect, or check the user's World ID account. Use when the user asks "what's my World ID?", requests their World ID identifier or continuity handle, or wants to link, sign in to, or verify their World ID account.
---

# World ID Account

1. Call `get_world_id_account` from the connected World ID MCP server with no arguments.
2. If authorization is required, let the host show its native login and consent flow.
   World ID sign-in creates or resolves the account. Do not ask for credentials,
   proofs, tokens, or account identifiers in chat, or construct an authorization URL.
3. After linking, call the tool again if the host has not retried it. Report success
   only when it returns `status: active` and `world_id_verified: true` without an error.
   When the user asks for their World ID, return `continuity_handle` and describe it as
   their sector-specific continuity handle, not a global or internal account ID. This
   confirms prior verification, not fresh human presence or that the agent is human.
4. If the user cancels or authorization fails, do not report a connected account.
   Explain the failure briefly; offer another attempt without repeatedly prompting.
