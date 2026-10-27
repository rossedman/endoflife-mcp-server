# Tools

Every tool the server registers, generated from the running server by
`tools/gen_tool_docs.py`. All of them are read-only: they only query endoflife.date and
never change anything. For worked examples with real output, see the
[tools guide](../tools.md).

## `product_list_all`

List the name of every product endoflife.date tracks (about 500).

This tool takes no parameters.

**Returns:** Product names, such as python, kubernetes and amazon-eks.

## `product_get_all`

Get a product with all of its release cycles and their support and end-of-life dates.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `product` | string | yes | Product name or alias, such as python, kubernetes or amazon-eks. |

**Returns:** The product: label, category, tags, links and every release cycle.

## `product_get_cycle`

Get one release cycle of a product, such as python 3.12.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `product` | string | yes | Product name or alias, such as python, kubernetes or amazon-eks. |
| `cycle` | string | yes | Release cycle name as listed in the product's releases, e.g. 3.12. |

**Returns:** The release cycle: release, support and end-of-life dates, LTS status and latest version.

## `product_get_latest`

Get the newest release cycle of a product.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `product` | string | yes | Product name or alias, such as python, kubernetes or amazon-eks. |

**Returns:** The latest release cycle, in the same shape as product_get_cycle.

## `category_list`

List the product categories, such as lang, os, database and framework.

This tool takes no parameters.

**Returns:** Category names.

## `category_list_products`

List the products in a category, such as every database endoflife.date tracks.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `category` | string | yes | A category name from category_list. |

**Returns:** A summary (name, label, aliases, category, tags) of each product.

## `tag_list`

List the product tags, such as linux-distribution, amazon or cncf.

This tool takes no parameters.

**Returns:** Tag names.

## `tag_list_products`

List the products with a tag, such as every managed Kubernetes service.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `tag` | string | yes | A tag name from tag_list. |

**Returns:** A summary (name, label, aliases, category, tags) of each product.
