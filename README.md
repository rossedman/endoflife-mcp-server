# endoflife-mcp-server

A server for the end-of-life website. Allows users to query software end-of-life information, including release dates, support timelines, and latest versions.

## Examples

Check out the examples below to see how to use the end-of-life MCP tool effectively.

<details>
    <summary>Get Newest 5 Versions Of Kubernetes</summary>
    
    > Can you get the newest 5 version of the Kubernetes product in endoflife and make a markdown table of dates

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
</details>

<details>
    <summary>Get Oldest Supported Versions Of Python</summary>

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
</details>

<details>
    <summary>Get Versions Of etcd That Will Be Support In 6 Months</summary>

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
</details>

<details>
    <summary>Compare Kubernets And EKS Versions</summary>

    > From endoflife, compare kubernetes and amazon-eks to see what versions overlap with support and will be supported at the same time

    ⏺ Comparison of Kubernetes and Amazon EKS support cycles:

    Overlapping Supported Versions (as of 2025-07-15):
    1. 1.33:
        - Kubernetes: Supported until 2026-06-28
        - Amazon EKS: Supported until 2026-07-29 (with extended support until 2027-07-29)
    2. 1.32:
        - Kubernetes: Supported until 2026-02-28
        - Amazon EKS: Supported until 2026-03-23 (with extended support until 2027-03-23)
    3. 1.31:
        - Kubernetes: Supported until 2025-10-28
        - Amazon EKS: Supported until 2025-11-26 (with extended support until 2026-11-26)
    4. 1.30:
        - Kubernetes: Supported until 2025-06-28
        - Amazon EKS: Supported until 2025-07-23 (with extended support until 2026-07-23)

    Note: Amazon EKS typically provides extended support beyond the standard Kubernetes support cycle, giving users additional time to upgrade.
</details>

## Setup

### Clone

```bash
git clone https://github.com/rossedman/endoflife-mcp-server.git
cd endoflife-mcp-server
```

### Install

```bash
uv venv
source .venv/bin/activate
uv sync
```

### Claude

```bash
claude mcp add -s user endoflife -- uv run --directory $(pwd) main.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
