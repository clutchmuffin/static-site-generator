import re

from textnode import TextNode, TextType


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    """Split plain-text nodes on a markdown-style inline delimiter.

    Each PLAIN node in `old_nodes` is divided by `delimiter` into alternating
    segments: text outside the delimiters becomes PLAIN nodes, and text between
    a pair of delimiters becomes a node of `text_type`. Non-plain nodes are
    passed through unchanged so already-converted segments are never re-split.

    Example:
        split_nodes_delimiter(
            [TextNode("This is **bold**", TextType.PLAIN)], "**", TextType.BOLD
        )
        # -> [TextNode("This is ", TextType.PLAIN),
        #     TextNode("bold", TextType.BOLD)]

    Args:
        old_nodes: The list of TextNodes to process.
        delimiter: The markdown delimiter to split on (e.g., "**", "*", "`").
            Must match exactly; partial matches are not treated specially.
        text_type: The TextType assigned to content found between delimiter pairs.

    Returns:
        A new list of TextNodes with delimited content converted to `text_type`.
        Input nodes are not modified.

    Raises:
        ValueError: If a PLAIN node contains an odd number of `delimiter`
            occurrences, meaning no matching closing delimiter exists.
    """
    new_nodes: list[TextNode] = []

    for node in old_nodes:
        # Only split plain-text nodes; pass everything else through untouched
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue

        split: list[str] = node.text.split(delimiter)

        # After splitting, only odd-numbered positions hold delimited text.
        # An even count means the closing delimiter is missing.
        if len(split) % 2 == 0:
            raise ValueError("Matching closing delimiter not found!")

        # Iterate though the list of split text, create either TEXT or given 'text_type' text nodes
        for i, chosen_text in enumerate(split):
            # Empty string, between two delimiters or beginning/end
            if chosen_text == "":
                continue
            # text_type node
            if i % 2 == 1:
                new_nodes.append(TextNode(chosen_text, text_type))
            # TEXT node
            else:
                new_nodes.append(TextNode(chosen_text, TextType.PLAIN))
    return new_nodes


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    """
    Extract all markdown image references from a string.

    Scans `text` for markdown image syntax and returns each match as an
    `(alt_text, url)` tuple, in order of appearance. Only images are matched;
    regular links (no leading "!") are ignored.

    Example:
        extract_markdown_images("![pic](img.png) and ![logo](logo.png)")
        # -> [("pic", "img.png"), ("logo", "logo.png")]

    Args:
        text: The raw markdown text to scan.

    Returns:
        A list of (alt_text, url) tuples. Empty list if no images found.
    """
    matches: list[tuple[str, str]] = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    """
    Extract all markdown link references from a string.

    Scans `text` for markdown link syntax and returns each match as an
    `(anchor_text, url)` tuple, in order of appearance. Image syntax is
    excluded, so "![alt](url)" does not produce a link match.

    Note:
        Call this AFTER extract_markdown_images when processing mixed text,
        or ensure image syntax is handled first to avoid mis-parsing.

    Example:
        extract_markdown_links("[boot](boot.dev) and [more](x.dev)")
        # -> [("boot", "boot.dev"), ("more", "x.dev")]

    Args:
        text: The raw markdown text to scan.

    Returns:
        A list of (anchor_text, url) tuples. Empty list if no links found.
    """
    matches: list[tuple[str, str]] = re.findall(
        r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text
    )
    return matches
