# Using the tools

The server gives your assistant eight read-only tools. You never call them yourself; you ask a question, the assistant chooses the tools, and this page shows what they return. The output below is copied from real calls to endoflife.date on 2026-10-27, so dates after that day will have moved on.

Every tool takes plain names. Product names are endoflife.date slugs such as `python`, `kubernetes` or `amazon-eks`, case-insensitive, and aliases such as `k8s` and `postgres` work too. For parameters and return shapes of each tool, see the [tools reference](reference/tools.md).

## Answer one question: a single release

`product_get_cycle` returns one release cycle of one product. This is the call behind "is Python 3.10 still supported?".

```json title="product_get_cycle(product: 'python', cycle: '3.10')"
{
  "name": "3.10",
  "releaseDate": "2021-10-04",
  "isLts": false,
  "isEol": true,
  "eolFrom": "2026-10-01",
  "isMaintained": false,
  "latest": {
    "name": "3.10.22",
    "date": "2026-10-01",
    "link": "https://www.python.org/downloads/release/python-31022/"
  },
  "isEoas": true,
  "eoasFrom": "2023-04-05",
  "custom": { "pep": "PEP-0619" }
}
```

Three fields carry the answer. `isEol` says whether security support has ended, `eolFrom` says when, and `isEoas` with `eoasFrom` say when active (bug-fix) support ended. Fields the product doesn't have, such as `codename` or `ltsFrom`, come back `null` and are omitted here.

!!! note "Null dates"
    A `null` date next to a `true` flag means the date is not known yet, not that it never happens.

## See the whole picture: every release of a product

`product_get_all` returns the product with all of its release cycles, newest first. Asked to compare Kubernetes versions, an assistant reads this and builds the table. These are the first five `releases` entries, trimmed to the date fields:

| Release | Released | Active until | End of life | Latest | Is EOL |
| --- | --- | --- | --- | --- | --- |
| 1.37 | 2026-08-26 | 2027-08-28 | 2027-10-28 | 1.37.1 | no |
| 1.36 | 2026-04-22 | 2027-04-28 | 2027-06-28 | 1.36.5 | no |
| 1.35 | 2025-12-17 | 2026-12-28 | 2027-02-28 | 1.35.9 | no |
| 1.34 | 2025-08-27 | 2026-08-27 | 2026-10-27 | 1.34.12 | no |
| 1.33 | 2025-04-23 | 2026-04-28 | 2026-06-28 | 1.33.13 | yes |

The response also carries the product's label, category, tags, links, a version command and package identifiers (purl, CPE), which is why it is the larger of the two calls.

## Use the newest release

`product_get_latest` is `product_get_all` cut down to the newest cycle. Here the alias `postgres` resolves to `postgresql`:

```json title="product_get_latest(product: 'postgres')"
{
  "name": "18",
  "releaseDate": "2025-09-25",
  "isLts": false,
  "isEol": false,
  "eolFrom": "2030-11-14",
  "isMaintained": true,
  "latest": {
    "name": "18.6",
    "date": "2026-08-11",
    "link": "https://www.postgresql.org/docs/release/18.6/"
  }
}
```

## Find the right name

When you don't know the slug, the assistant lists names or browses by category and tag.

| Tool | What it returns | Real count |
| --- | --- | --- |
| `product_list_all` | Every product name | 486 |
| `category_list` | Category names | 9 |
| `tag_list` | Tag names | 88 |
| `category_list_products` | A summary of each product in a category | 27 in `database` |
| `tag_list_products` | A summary of each product with a tag | 4 in `managed-kubernetes` |

The nine categories are `framework`, `server-app`, `service`, `lang`, `os`, `app`, `database`, `device` and `standard`. A product summary is small:

```json title="tag_list_products(tag: 'managed-kubernetes'), second entry"
{
  "name": "amazon-eks",
  "label": "Amazon EKS",
  "aliases": ["eks", "amazon-elastic-kubernetes-service"],
  "category": "service",
  "tags": ["amazon", "managed-kubernetes", "service"]
}
```

The four managed Kubernetes services are `alibaba-ack`, `amazon-eks`, `azure-kubernetes-service` and `google-kubernetes-engine`. Comparing one of them with `kubernetes` is a question the assistant answers with two `product_get_all` calls.

## When a name is wrong

A typo does not end in a dead end. The server looks the name up against every product name and alias and puts the closest matches in the error, which the model sees:

```console
product_get_all(product: "pyhton")
Error executing tool product_get_all: endoflife.date has no product 'pyhton'.
Did you mean: python, photon, iphone, phoenix-framework?
```

The assistant retries with `python`. Other mistakes get equally plain messages:

```console
product_get_cycle(product: "python", cycle: "9.9")
Error executing tool product_get_cycle: endoflife.date has no release '9.9' of product 'python'.

product_get_cycle(product: "Python!", cycle: "3.12")
Error executing tool product_get_cycle: 'python!' is not a valid product name: use lowercase
letters, digits, '.', '_', '+' and '-', starting with a letter or digit.
```

Names are checked before any request is made, so a model cannot steer a request to a different endpoint by passing a crafted name. If endoflife.date is rate limiting or unreachable, the error says so and, for rate limits, how long to wait.

## Prompts that work well

- "Which of the Python versions we support in `pyproject.toml` are past end of life?"
- "We upgrade every six months. Which etcd versions will still be supported then?"
- "List every database endoflife.date tracks and flag the ones with a release going EOL this year."
- "Compare Kubernetes and Amazon EKS support windows for the last four versions."
