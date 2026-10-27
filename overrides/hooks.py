"""MkDocs hooks: make the root CONTRIBUTING.md and SECURITY.md links work inside the site.

The two files are included into the docs with a ``--8<-- "FILE.md"`` snippet directive, but
their links are written for the repository root (``SECURITY.md``, ``.github/CODEOWNERS``).
Markdown extensions run after page hooks, so this hook performs the include itself, with the
links rewritten to the pages and GitHub URLs that exist on the site.
"""

from pathlib import Path
from typing import Any

REPO = "https://github.com/rossedman/endoflife-mcp-server"

REWRITES = {
    "](SECURITY.md": "](security.md",
    "](CODE_OF_CONDUCT.md)": f"]({REPO}/blob/main/CODE_OF_CONDUCT.md)",
    "](.github/CODEOWNERS)": f"]({REPO}/blob/main/.github/CODEOWNERS)",
    "](CONTRIBUTING.md": "](contributing.md",
}


def on_page_markdown(markdown: str, page: Any, **kwargs: Any) -> str:
    """Include a root file into its docs page, with the links pointing at the site.

    Args:
        markdown: The page source, holding the snippet directive.
        page: The page being built.
        **kwargs: Other hook arguments, unused.

    Returns:
        The page source with the root file included and its links pointing at the site.
    """
    for name in ("CONTRIBUTING.md", "SECURITY.md"):
        directive = f'--8<-- "{name}"'
        if directive not in markdown:
            continue
        text = Path(name).read_text(encoding="utf-8")
        for old, new in REWRITES.items():
            text = text.replace(old, new)
        markdown = markdown.replace(directive, text)
    return markdown
