---
name: world-id-developer
description: Register a sandbox app with World ID or configure its OIDC client, callback URLs, and logo. Use for developer onboarding and Sign in with World ID integration setup, including explaining how to submit the app's benefit listing. Not for checking a person's World ID or finding benefits to use.
---

# World ID developer

Use this plugin's MCP connection at `https://sandbox.auth.world.org/mcp`.
Perform registration and configuration through its tools. Browser control is
not required: the developer signs in and approves credential requests themselves.
Keep all operations in sandbox; do not switch to staging or production.

## Connect the developer account

Call `get_portal_account` to check the connected developer identity. Portal tools
require `developer-portal:manage`, authorized through Google portal sign-in;
they do not require a World ID or `world-id:read`.

If authorization is needed, use the host's MCP authorization flow and follow the
tool's scope challenge, preserving existing scopes. If the host cannot complete it:

- Codex users can run `codex mcp login world-id-sandbox --scopes developer-portal:manage`
  in their terminal, complete Google sign-in and consent, then start a new Codex
  session. If they also use account/benefit tools, use
  `--scopes world-id:read,developer-portal:manage` to authorize both flows.
- Claude Code users can select the sandbox server in `/mcp` and authenticate
  for the requested developer-portal scope.

Resume after reconnection. Do not retry an authorization failure in a loop or
ask for tokens in chat.

## Register an app

1. Call `list_oidc_clients` before creating a client. If the intended app already
   exists, use its `clientId`; ask which app when the match is ambiguous.
2. Read `get_idp_guide` with `{"id":"oidc"}` for the current registration and
   integration requirements. Collect the app name, exact callback URLs, optional
   public logo URL, and client authentication method. Use the project's existing
   configuration where available; ask for missing deployment URLs rather than
   inventing them. Registration requires a confidential backend. Use
   `client_secret_basic` when the developer has no preference and their backend
   supports it; also supported are `client_secret_post` and `private_key_jwt`.
3. Check the registration details:

   - Sandbox callbacks must be HTTPS and match exactly; HTTP localhost and
     wildcard callbacks are not accepted. A device-only client still needs a
     registered redirect URI.
   - A logo is an optional public HTTPS PNG or JPEG, at most 512×512 pixels and
     256 KiB. Ask for a hosted URL if the developer only has a local file.
   - Multiple callback hostnames need a public HTTPS `sectorIdentifierUri`
     whose JSON array lists all exact callback URLs. The sector and client
     authentication method cannot be changed after registration.
   - For `private_key_jwt`, supply only public JWKS. Private keys stay with the
     developer's backend; never put secrets or private keys in chat or MCP calls.

4. Call `request_oidc_client_registration` with a fresh UUID `requestId`, `name`,
   `redirectUris`, `tokenEndpointAuthMethod`, and any `logoUri`,
   `sectorIdentifierUri`, or public `jwks` needed. Retain the request ID. If the
   response is lost, check `get_portal_credential_request` first; any retry must
   reuse the same request ID and identical inputs, not create a duplicate request.
5. Give the developer the returned `portalUrl` unchanged and ask them to review
   and approve it in their browser. The app does not exist until approval.
   Any generated secret is shown only there; the developer saves it directly in
   backend configuration. Never ask them to paste it into chat or read it through
   browser automation.
6. Use `get_portal_credential_request` with the same `requestId` after the
   developer responds, or poll sparingly while awaiting approval. Bound polling
   by `request.expiresAt` (requests last 20 minutes). Stop on `completed`,
   `denied`, `expired`, or `revoked`, and surface tool errors. Only `completed`
   confirms success; use `request.result.client` for the public client details.
   Report a terminal failure rather than silently starting another registration.

Return the client ID, sandbox issuer `https://sandbox.auth.world.org`, registered
callbacks, and authentication method. Link to the client's portal page. If the
developer also asks for implementation, use the `oidc` guide, or `federation` for
an existing identity provider, and work within their app's existing auth setup.

## Configure an existing app

Read `get_oidc_client` first. `update_oidc_client` replaces the configuration:
send `clientId`, `name`, `redirectUris`, `sectorIdentifierUri`, `status`, and
`logoUri`, preserving values the developer did not ask to change. Use `null` to
preserve the logo or an empty string only when asked to remove it. Preserve the
immutable sector. Report a change only after the tool succeeds; reads may lag.

## Submit a benefit listing

App registration does not publish a benefit. The current MCP has no catalog
submission tool. Direct the developer to
`https://sandbox.auth.world.org/portal/clients/{clientId}?tab=catalog` using the
actual client ID: save the listing name, description, and app URL, then submit
for review. Only the owner of an active app can submit. A separate authorized
reviewer who is not an app member must approve it; approval publishes the listing.
Do not report a pending submission as approved or published.
