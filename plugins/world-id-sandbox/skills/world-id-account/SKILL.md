---
name: world-id-account
description: Check the user's World ID account or explain connection setup. Use when the user asks "what's my World ID?", requests their World ID identifier or continuity handle, or wants to connect or check their World ID account.
---

# World ID Account

This plugin uses the sandbox environment at `https://sandbox.auth.world.org/mcp`.
Use its bundled MCP connection, not a staging or production World ID connection.

1. Call `get_world_id_account` from this plugin's World ID MCP server with no arguments.
2. If authorization is required:
   - Do not claim a login prompt opened unless you have evidence. An authentication
     challenge or "Sign in with World ID" tool result alone is not that evidence.
   - Do not execute MCP login commands or start a login subprocess yourself.
   - For Codex CLI, tell the user to exit the session, run
     `codex mcp login world-id-sandbox --scopes mcp:read` in their terminal,
     complete browser sign-in and consent, and wait for the command to report
     success before launching `codex` again. This is a user setup instruction,
     not a command for the agent to execute. If login already succeeded in this
     session, ask them to relaunch Codex without logging in again.
   - For Claude Code, ask the user to enter `/mcp`, select this plugin's sandbox
     server, and authenticate. For other hosts, direct them to that host's
     supported MCP authentication controls.
   - The plugin already configures its MCP server; do not add a duplicate.
     Never construct an authorization URL or ask for credentials, proofs, tokens,
     or account identifiers in chat.
   - Stop and let the user complete setup. Do not repeatedly call the tool to
     trigger a prompt or describe an authorization-required result as proof that
     a completed browser login failed.
3. When the user asks to check again after setup, call the tool. Report success
   only when it returns `status: active` and `world_id_verified: true` without an error.
   When the user asks for their World ID, return `continuity_handle` and describe it as
   their sector-specific continuity handle, not a global or internal account ID. This
   confirms prior verification, not fresh human presence or that the agent is human.
4. If the user cancels or authorization fails, do not report a connected account.
   Explain the failure briefly; offer another attempt without repeatedly prompting.
