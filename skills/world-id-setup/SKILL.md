---
name: world-id-setup
description: Set up the World ID plugin with a dedicated Proof of Human verification step, then show available benefits. Use when the user runs plugin setup or asks to get started with World ID.
---

# Set up World ID

Use the bundled sandbox World ID MCP at `https://sandbox.auth.world.org/mcp`.
Sandbox verification is separate from production. Honor an explicit request to
browse benefits without signing in; setup is not a prerequisite for discovery.

Introduce setup briefly: "Verify you're human with World ID, then explore what
it unlocks." Running setup authorizes starting World ID connection, but does not
authorize connecting partner accounts or claiming an offer.

Check `get_world_id_account` with no arguments. An error-free response with
`status: active` and `world_id_verified: true` establishes verified connection;
do not infer verification from installation, browser navigation, or a partner login.
If already verified, acknowledge it and continue without asking for another proof.
If authorization is required or the valid account status is not verified, explain
that the user completes World ID sign-in in their browser and start the host's
MCP authorization flow. Request `world-id:read` and preserve existing scopes.
In Codex, when native connection controls are unavailable, run
`codex mcp login world-id-sandbox --scopes world-id:read` (include existing scopes
if known). In Claude Code, use this server's authentication flow in `/mcp`.
Show the returned authorization URL if the browser does not open.

After successful authorization, check `get_world_id_account` again. If the first
check still needs authentication, explain that the current chat may have stale
credentials and ask the user to continue setup in a new chat. Stop without
repeating login or declaring verification failed. Stop on a declined or failed
login. For invalid status fields or other errors, say verification could not be
confirmed. Never declare setup complete without the verified account response.

Once verified, say "You're verified. Here's what you can do with World ID."
Call `get_benefits` and offer concrete next actions drawn only from returned
listings. An empty or unavailable catalog does not undo successful verification;
report that benefits are unavailable without inventing offers. Listings do not
establish eligibility or redemption. Let the user choose an action before
starting partner authorization; partner consent remains separate from World ID
verification. Report a claim as successful only after partner confirmation.

Never request or disclose credentials, proofs, tokens, continuity handles,
nullifiers, biometric data, or other private identifiers, including raw errors.
