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


def block_to_block_type(block: str) -> BlockType:
    """
    Classify a markdown block into its block type.

    Determines the type of a single markdown block based on its syntax:
    headings start with 1-6 `#` characters followed by a space, code blocks
    are wrapped in triple backticks, every line of a quote starts with `>`,
    every line of an unordered list starts with `- `, and every line of an
    ordered list starts with an incrementing number followed by `. `. Blocks
    matching none of these conditions are treated as paragraphs.

    Args:
        block: A single block of markdown text. Leading and trailing
            whitespace are assumed to have already been stripped.

    Returns:
        The BlockType of the given block.
    """

    # HEADINGS
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING

    # CODE
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    lines: list[str] = block.split("\n")

    # QUOTE
    for line in lines:
        if not line.startswith(">"):
            break
    else:
        return BlockType.QUOTE

    # UNORDERED LIST
    for line in lines:
        if not line.startswith("- "):
            break
    else:
        return BlockType.UNORDERED_LIST

    # ORDERED LIST
    for index, line in enumerate(lines, start=1):
        if not line.startswith(f"{index}. "):
            break
    else:
        return BlockType.ORDERED_LIST

    # PARAGRAPH
    return BlockType.PARAGRAPH
