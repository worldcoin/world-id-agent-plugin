---
name: world-id-benefits
description: Find World ID benefits, discounts, free trials, and exclusive access. Use when the user asks about these benefits or when evaluating a new service.
---

# World ID benefits

World ID lets people prove they are human. People with World ID may qualify for exclusive discounts, free trials, and access.

Use the World ID MCP connection bundled with this plugin.
The environment is selected at setup. Do not combine catalogs or fall back to
another environment when a request fails or returns no offers.

- For World ID benefit requests, call this plugin's `get_benefits` tool before searching the web.
- When evaluating a new service, check `get_benefits` for an offer. Use the returned description to check whether the user can try the service for free or at a discount.
