---
name: world-id-benefits
description: Find World ID partner benefits and help use them through connected partner tools. Use for benefits, discounts, free trials, exclusive access, evaluating a service, or follow-up questions about a named partner such as "what can I do with Maître?".
---

# World ID benefits

World ID lets people prove they are human. People with World ID may qualify for exclusive discounts, free trials, and access.

## Discover benefits

Use `get_benefits` from this plugin's `https://sandbox.auth.world.org/mcp`
connection before searching the web for World ID benefits or offers from a new
service. Reuse a relevant catalog result already in the conversation for a
partner follow-up. Do not substitute a staging or production World ID catalog
if the sandbox catalog is empty or unavailable. If authorization is required,
refer to the README's World ID setup instructions and stop retrying that tool.

Describe only the benefit the catalog returns. Exclusive access need not be a
discount or free trial. A listing does not confirm eligibility, live inventory,
or successful redemption.

## Continue with a named partner

Keep using this skill for follow-ups such as "what can I do with Maître?" or
"help me use that benefit", even when the user does not repeat "World ID".

1. Check the available tools for the selected partner. If the host supports
   deferred tool discovery, search for that partner's MCP tools before using
   web search or browser automation. Inspect their descriptions and schemas;
   do not guess tool names or arguments from the catalog listing.
2. For a capability question, explain what the listing and connected tools
   support. For live availability, offers, or account information, use the
   appropriate read-only partner tool. Do not attempt a booking or require
   sign-in merely to explain capabilities.
3. Use connected partner MCP tools for supported actions, following their
   approval and authentication requirements. Do not substitute a website or
   public partner listing for data the tools can provide. Browsing remains
   appropriate when the user explicitly requests it, for a returned sign-in or
   verification link, or for a documented redemption path without MCP support.
4. If no partner tools are available, explain that this plugin bundles only the
   sandbox World ID MCP server. A catalog listing does not install or authorize
   the partner's MCP connection. Help connect the partner using a verified
   endpoint from its setup documentation or catalog metadata; never infer an
   MCP URL from a homepage. Do not claim the partner MCP is connected until a
   tool check succeeds.

For Maître, available MCP tools may include `list_seats`, `claim_seat`,
`my_reservations`, `cancel_reservation`, and `wait_for_verification`. Confirm
which are exposed in the current session. Use `list_seats` for current partner
tables; available seats are not evidence of a discount. Submit a booking claim
only after approval of the table details, and distinguish a pending claim from
a confirmed restaurant reservation.

## Separate partner sign-in from verification

World ID catalog authorization does not sign the user into a partner service or
satisfy that partner's verification requirements.

- **Partner MCP authentication required:** use the host's explicit MCP login
  flow for that partner. In Codex CLI, use `codex mcp login <server-name>` with
  the actual configured partner server name. In Claude Code, use `/mcp` to
  select and authenticate that server. Do not announce a sign-in popup or URL
  unless the client supplies one, or repeatedly call a protected tool to open
  it. After sign-in, use a read-only partner tool to check the connection.
- **Maître World ID step-up:** a `verification_required` result containing
  `verification_url` and `handoff` means the MCP request authenticated but
  additional verification is needed. Show the exact returned URL as a clickable
  link; this is not an automatic MCP popup. Use the same Google account as the
  Maître connection, then follow the returned `wait_for_verification` workflow.
  Do not restart OAuth or invent a verification URL. Retry only the already
  approved booking after a verified result; stop waiting on timeout or error.
