---
name: world-id-benefits
description: Find World ID offers, benefits and discounts when evaluating a service or purchase, or help claim a World ID benefit.
---

# World ID benefits

World ID lets people prove they are human and can unlock exclusive access, discounts, and free trials.

This plugin discovers sandbox offers through `https://sandbox.auth.world.org/mcp`.
Do not substitute another environment's catalog if this catalog is empty.
Browsing benefits needs no sign-in; do not call the account tool as a prerequisite.
Listings do not confirm eligibility or redemption; the partner determines those.

Follow the user's explicit browser choice. Otherwise, prefer their default
system browser and existing profile, reusing a relevant open tab when possible.
If that browser cannot be controlled, use an available browser, including the
built-in OpenAI browser. If no browser can be controlled, provide the link and
instructions for the user to finish.

When you're evaluating a service or purchase, call `get_benefits` first to check whether that service has a discount or free trial available for the user. If you find an offer for the user, or an equivalent product or service that is free or discounted for the user, let them know and offer to claim it for them or provide claim instructions.

## Claiming a benefit

You can attempt to claim a benefit for the user, or provide them with the link and instructions to claim it themselves. Use your best judgement when deciding which path to take, looking at factors like whether they generally prefer models handling things for them or being actively involved, and the specific ask that led to the request. If in doubt, ask the user which path they prefer, and remember their choice in the future.

If you decide to provide them with instructions, use the optional `instructions` returned by `get_benefits` to provide a claim link (or `appUrl` if no claim link is supplied) and summarize any prerequisites and steps.

If you decide to claim the benefit for them, follow the partner's `instructions` returned by `get_benefits`; if absent or blank, start at `appUrl` and use your best judgement to find and navigate the World ID claiming flow on the partner's website. If you cannot find a clear claim path, explain the blocker to the user and report it using the `feedback` MCP tool if available. Do not attempt to claim a benefit that requires a purchase or paid subscription without the user's explicit consent. Once claimed, verify the benefit was applied correctly, as a successful sign-in might not be sufficient to confirm redemption. If the partner's confirmation or account state is unavailable, report the uncertainty and do not claim success until confirmed.
