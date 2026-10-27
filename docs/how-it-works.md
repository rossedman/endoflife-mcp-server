# How it works

Between your question and the answer there are three hops and one rule: nothing is remembered, so every answer is read from endoflife.date at the moment you ask.

<figure class="diagram" markdown>
![Three boxes joined by arrows. Your assistant sends an MCP tool call such as product_get_cycle for python 3.10 to endoflife-mcp-server. The server validates the name, resolves aliases, calls the endoflife.date API live and suggests names on a miss. endoflife.date answers with fields such as isEol true, eolFrom 2026-10-01 and latest 3.10.22.](assets/how-it-works.png)
</figure>

## The three parts

**Your assistant** is any MCP client. When it connects, the server hands over a short set of instructions (start with `product_get_all`, names are slugs, dates are ISO 8601) and the list of eight tools, so the model knows how to ask.

**The server** is a thin layer, on purpose. It validates names, calls the API, and shapes the result. It has no database and no cache.

**endoflife.date** is the community-maintained source. The server uses its v1 API through a client generated from the vendored OpenAPI spec, so responses are typed rather than parsed by hand.

## What the server adds

- **Name checking.** Names reach the model from anywhere, so each is trimmed, lowercased and matched against the characters real product names use before it is placed in a URL.
- **Aliases.** `k8s` and `postgres` resolve to the product the API knows.
- **Suggestions on a miss.** A wrong product name returns the closest real ones in the error text, so the model corrects itself without asking you.
- **Plain errors.** Rate limits, timeouts and unexpected answers become short messages the model can relay, instead of stack traces.
- **A polite user agent.** Every request carries the server's name and version, so endoflife.date can see where traffic comes from.

## What it does not do

It does not cache, so a burst of questions is a burst of requests. It does not scan your project for versions; your assistant does that, then asks this server what each version's dates are. And it does not write anywhere: every tool is read-only.
