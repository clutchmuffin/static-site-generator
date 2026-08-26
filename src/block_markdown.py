from enum import Enum


class BlockType(Enum):
    """
    Enumeration of supported markdown block types.

    Each member represents a kind of structural unit (e.g., heading, quote,
    list) that a markdown document can be split into, used to decide how
    each block is rendered as HTML.
    """

    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown: str) -> list[str]:
    """Split a markdown document into blocks separated by blank lines.

    Blocks are separated by one or more blank lines. Each returned block is
    stripped of surrounding whitespace, and empty blocks are dropped.

    Args:
        markdown: The raw markdown document as a string.

    Returns:
        A list of non-empty, whitespace-stripped markdown blocks.
    """
    lines: list[str] = markdown.split("\n\n")
    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            continue
        new_lines.append(stripped)
    return new_lines
