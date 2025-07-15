# endoflife-mcp-server

A server for the end-of-life MCP tool.

```
>  Can you get the newest 5 version of the Kubernetes product in endoflife and make a markdown table of dates

⏺ Here's a markdown table of the 5 newest Kubernetes versions:

  | Version | Release Date | Latest Version | Latest Release Date | End of Life | Support Ends |
  |---------|--------------|----------------|---------------------|-------------|--------------|
  | 1.33    | 2025-04-23   | 1.33.2         | 2025-06-17          | 2026-06-28  | 2026-04-28   |
  | 1.32    | 2024-12-11   | 1.32.6         | 2025-06-17          | 2026-02-28  | 2025-12-28   |
  | 1.31    | 2024-08-13   | 1.31.10        | 2025-06-17          | 2025-10-28  | 2025-08-28   |
  | 1.30    | 2024-04-17   | 1.30.14        | 2025-06-17          | 2025-06-28  | 2025-04-28   |
  | 1.29    | 2023-12-13   | 1.29.15        | 2025-03-11          | 2025-02-28  | 2024-12-28   |

  Key observations:
  - No versions are marked as Long Term Support (LTS)
  - Each version is typically supported for about 14-16 months
  - Latest patch releases are consistently dated 2025-06-17 for the top 4 versions
```

```
> Can you return the oldest versions of python that are still supported in endoflife

⏺ Here are the oldest Python versions that are still supported:

  | Version | Release Date | End of Life | Latest Version | Support Ends |
  |---------|--------------|-------------|----------------|--------------|
  | 3.8     | 2019-10-14   | 2024-10-07  | 3.8.20         | 2021-05-03   |
  | 3.9     | 2020-10-05   | 2025-10-31  | 3.9.23         | 2022-05-17   |
  | 3.10    | 2021-10-04   | 2026-10-31  | 3.10.18        | 2023-04-05   |
  | 3.11    | 2022-10-24   | 2027-10-31  | 3.11.13        | 2024-04-01   |

  Notes:
  - Python 3.8 is the oldest version still receiving updates (until October 2024)
  - None of these versions are marked as Long Term Support (LTS)
  - Support for older versions typically lasts around 5 years
  - Newer versions (3.9-3.11) are still receiving updates
```

```
> We only upgrade every 6 months, what version of etcd will still be supported in 6 months when we upgrade, check endoflife

⏺ In 6 months, you will have two supported etcd versions:

  1. etcd 3.5
    - Release Date: 2021-06-15
    - Latest Version: 3.5.21
    - Latest Release Date: 2025-03-27
    - Not End of Life
  2. etcd 3.6
    - Release Date: 2025-05-15
    - Latest Version: 3.6.2
    - Latest Release Date: 2025-07-10
    - Not End of Life

  Note: etcd 3.4 will reach its End of Life on 2025-05-15, so it won't be recommended for use after that date.

  Recommendation: Plan to upgrade to either version 3.5 or 3.6 when you do your upgrade in 6 months.
```

## Install

```bash
claude mcp add -s user endoflife -- uv run --directory $(pwd) main.py
```

## Setup Environment

```bash
brew install uv
uv venv
source .venv/bin/activate
uv sync
```