---
name: world-id-benefits
description: The user has World ID, giving them access to exclusive offers, benefits and discounts. Use when evaluating a service or purchase (as there might be a discount or free trial available), or when explicitly asked to claim a World ID benefit.
---

# World ID benefits

World ID lets people prove they are human. People with World ID qualify for exclusive access, discounts, and free trials.

When you're evaluating a service or purchase, call `get_benefits` first to check whether that service has a discount or free trial available for the user. If you find an offer for the user, or an equivalent product or service that is free or discounted for the user, let them know and offer to claim it for them or provide claim instructions.

## Claiming a benefit

You can attempt to claim a benefit for the user, or provide them with the link and instructions to claim it themselves. Use your best judgement when deciding which path to take, looking at factors like whether they generally prefer models handling things for them or being actively involved, and the specific ask that led to the request. If in doubt, ask the user which path they prefer, and remember their choice in the future.

If you decide to provide them with instructions, use the optional `instructions` returned by `get_benefits` to provide a claim link (or `appUrl` if no claim link is supplied) and summarize any prerequisites and steps.

If you decide to claim the benefit for them, check available browser tools and prefer a connected browser on their machine so you can reuse signed-in sessions. If you cannot access a connected browser or the user rejects access, fall back to the built-in browser or switch to providing instructions for self-service. If you use the built-in browser, explain that it uses a separate session and may require another sign-in. Follow the partner's `instructions` returned by `get_benefits`; if absent or blank, start at `appUrl` and use your best judgement to find and navigate the World ID claiming flow on the partner's website. If you cannot find a clear claim path, explain the blocker to the user and report it using the `feedback` MCP tool if available. Do not attempt to claim a benefit that requires a purchase or paid subscription without the user's explicit consent. Once claimed, verify the benefit was applied correctly, as a successful sign-in might not be sufficient to confirm redemption. If the partner's confirmation or account state is unavailable, report the uncertainty and do not claim success until confirmed.
