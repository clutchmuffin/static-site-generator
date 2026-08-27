from enum import Enum

from htmlnode import HTMLNode
from inline_markdown import text_to_textnodes
from parentnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node


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
    lines: list[str] = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING

    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    if all(lines[i].startswith(f"{i + 1}. ") for i in range(len(lines))):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown: str) -> ParentNode:
    """
    Convert a full markdown document into a tree of HTML nodes.

    Splits the document into blocks, classifies each block, and renders every
    block as the appropriate HTML node: headings become `h1`-`h6`, code blocks
    become `pre > code`, quotes become `blockquote`, lists become `ul`/`ol`
    with `li` children, and everything else becomes a `p`. Inline formatting
    inside text-bearing blocks is parsed into child nodes. All block nodes are
    wrapped in a single root `div`.

    Args:
        markdown: The raw markdown document as a string.

    Returns:
        A ParentNode representing the full document, rooted at a `div`.
    """
    blocks: list[str] = markdown_to_blocks(markdown)

    top_div_children: list[HTMLNode] = []

    for block in blocks:
        block_type: BlockType = block_to_block_type(block)

        match block_type:
            case BlockType.HEADING:
                top_div_children.append(heading_to_html_node(block))

            case BlockType.CODE:
                top_div_children.append(code_to_html_node(block))

            case BlockType.QUOTE:
                top_div_children.append(quote_to_html_node(block))

            case BlockType.UNORDERED_LIST:
                top_div_children.append(unordered_list_to_html_node(block))

            case BlockType.ORDERED_LIST:
                top_div_children.append(ordered_list_to_html_node(block))

            case BlockType.PARAGRAPH:
                top_div_children.append(paragraph_to_html_node(block))

    div_parent_node: ParentNode = ParentNode("div", top_div_children)
    return div_parent_node


def heading_to_html_node(block: str) -> ParentNode:
    """
    Build the HTML node for a heading block.

    Args:
        block: A heading block (e.g., "## Title").

    Returns:
        A ParentNode with the tag `h1`-`h6` matching the heading level.
    """
    sections: list[str] = block.split(" ", maxsplit=1)
    h_count: int = sections[0].count("#")
    h_tag: str = f"h{h_count}"
    h_text: str = sections[1]
    h_children: list[HTMLNode] = text_to_children(h_text)

    return ParentNode(h_tag, h_children)


def code_to_html_node(block: str) -> ParentNode:
    """
    Build the HTML node for a code block.

    Args:
        block: A fenced code block (wrapped in triple backticks).

    Returns:
        A `pre` ParentNode wrapping a `code` LeafNode of the inner text.
    """
    c_tag = "pre"
    c_text: str = block.split("```")[1].strip()
    c_text_node = TextNode(c_text, TextType.CODE)
    c_html_node: HTMLNode = text_node_to_html_node(c_text_node)

    return ParentNode(c_tag, [c_html_node])


def quote_to_html_node(block: str) -> ParentNode:
    """
    Build the HTML node for a quote block.

    Args:
        block: A quote block where every line starts with `>`.

    Returns:
        A `blockquote` ParentNode containing the quote's inline content.
    """
    q_tag: str = "blockquote"
    q_lines: list[str] = block.strip().split("\n")
    q_lines_non_arrow: list[str] = [line[1:].strip() for line in q_lines]
    q_text: str = "\n".join(q_lines_non_arrow)
    q_children: list[HTMLNode] = text_to_children(q_text)

    return ParentNode(q_tag, q_children)


def unordered_list_to_html_node(block: str) -> ParentNode:
    """
    Build the HTML node for an unordered list block.

    Args:
        block: A block where every line starts with `- `.

    Returns:
        A `ul` ParentNode containing one `li` child per list item.
    """
    ul_tag: str = "ul"
    ul_lines: list[str] = block.strip().split("\n")
    ul_lines_undash: list[str] = [line[2:].strip() for line in ul_lines]
    ul_children: list[HTMLNode] = line_to_list_item_parent_nodes(ul_lines_undash)

    return ParentNode(ul_tag, ul_children)


def ordered_list_to_html_node(block: str) -> ParentNode:
    """
    Build the HTML node for an ordered list block.

    Args:
        block: A block where every line starts with an incrementing number.

    Returns:
        An `ol` ParentNode containing one `li` child per list item.
    """
    ol_tag: str = "ol"
    ol_lines: list[str] = block.strip().split("\n")
    ol_lines_unindex: list[str] = [line.split(". ", 1)[1].strip() for line in ol_lines]
    ol_children: list[HTMLNode] = line_to_list_item_parent_nodes(ol_lines_unindex)

    return ParentNode(ol_tag, ol_children)


def paragraph_to_html_node(block: str) -> ParentNode:
    """
    Build the HTML node for a paragraph block.

    Args:
        block: A plain paragraph block.

    Returns:
        A `p` ParentNode containing the block's inline content.
    """
    p_tag: str = "p"
    p_children: list[HTMLNode] = text_to_children(block)

    return ParentNode(p_tag, p_children)


def text_to_children(text: str) -> list[HTMLNode]:
    """
    Convert a string of inline markdown into a list of HTML nodes.

    Runs the inline parsing pipeline to produce TextNodes, then maps each one
    to its corresponding HTML node via `text_node_to_html_node`.

    Args:
        text: The inline markdown text to convert.

    Returns:
        A list of HTML nodes (typically LeafNodes) representing the text.
    """
    text_nodes: list[TextNode] = text_to_textnodes(text)
    html_nodes: list[HTMLNode] = [text_node_to_html_node(node) for node in text_nodes]
    return html_nodes


def line_to_list_item_parent_nodes(lines: list[str]) -> list[HTMLNode]:
    """
    Convert stripped list item lines into `li` parent nodes.

    Each line is parsed for inline formatting and wrapped in a `ParentNode`
    with the `li` tag.

    Args:
        lines: A list of list item text lines (already stripped of list markers).

    Returns:
        A list of `li` ParentNodes, one per line.
    """
    line_html_nodes: list[HTMLNode] = []
    for line in lines:
        li_parent_node: ParentNode = ParentNode("li", text_to_children(line))
        line_html_nodes.append(li_parent_node)
    return line_html_nodes
