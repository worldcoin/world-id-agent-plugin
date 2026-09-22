---
name: world-id-benefits
description: Find World ID benefits, discounts, free trials, and exclusive access. Use when the user asks about these benefits or when evaluating a new service.
---

# World ID benefits

World ID lets people prove they are human. People with World ID may qualify for exclusive discounts, free trials, and access.

This plugin discovers sandbox offers through `https://sandbox.auth.world.org/mcp`.
Do not substitute a staging or production catalog if the sandbox catalog is empty.

- For World ID benefit requests, call this plugin's `get_benefits` tool before searching the web.
- When evaluating a new service, check `get_benefits` for an offer. Use the returned description to check whether the user can try the service for free or at a discount.
