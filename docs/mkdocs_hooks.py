"""MkDocs hooks for generated API documentation."""

import re

from mkdocs.plugins import event_priority  # type: ignore[import-not-found]


_BUILDING_BLOCK_PAGE = 'api/hpccm/building_blocks/README.md'
_SHORT_CROSS_REFERENCE = re.compile(r'\]\(#([A-Za-z_]\w*)\)')


@event_priority(-100)
def on_page_markdown(markdown, page, **kwargs):
    """Expand short building block anchors generated from docstrings."""

    if page.file.src_uri != _BUILDING_BLOCK_PAGE:
        return markdown

    return _SHORT_CROSS_REFERENCE.sub(
        r'](#hpccm.building_blocks.\1)',
        markdown
    )
