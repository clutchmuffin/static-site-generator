import re

from textnode import TextNode, TextType


def text_to_textnodes(text: str) -> list[TextNode]:
    """
    Convert a string of inline markdown into a list of TextNodes.

    Runs the full inline parsing pipeline: images and links are split out
    first, then bold, italic, and code delimiters. Each step operates only
    on remaining PLAIN nodes, so already-converted nodes are left untouched.

    The order is significant. Image and link syntax must be handled before
    delimiter splitting, since their brackets would otherwise be treated as
    plain text. Bold must be split before italic so that "**" pairs are not
    seen as empty italic segments.

    Example:
        text_to_textnodes("This is **bold** and _italic_")
        # -> [TextNode("This is ", TextType.PLAIN),
        #     TextNode("bold", TextType.BOLD),
        #     TextNode(" and ", TextType.PLAIN),
        #     TextNode("italic", TextType.ITALIC)]

    Args:
        text: The raw inline markdown string to convert.

    Returns:
        A new list of TextNodes representing the parsed inline content.

    Raises:
        ValueError: If any delimiter appears without a matching closer.
    """
    starter = TextNode(text, TextType.PLAIN)
    nodes = split_nodes_image([starter])
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    return nodes


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


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    """
    Split plain-text nodes around Markdown image references.

    Scans each plain-text node for image syntax, replacing each image reference
    with an `IMAGE` node and preserving surrounding content as `TEXT` nodes.
    Non-text nodes are returned unchanged.

    Args:
        old_nodes: The list of text nodes to process.

    Returns:
        A list of text and image nodes in their original order.
    """
    new_nodes: list[TextNode] = []

    for node in old_nodes:
        # Only plain text nodes can contain markdown image syntax.
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue

        text_to_process: str = node.text

        images: list[tuple[str, str]] = extract_markdown_images(node.text)

        # With no images, preserve the original node unchanged.
        if len(images) == 0:
            new_nodes.append(node)
            continue

        for alt_text, url in images:
            # Split once per the latest image markdown so later images remain in the unprocessed text.
            image_markdown: str = f"![{alt_text}]({url})"
            sections: list[str] = text_to_process.split(image_markdown, maxsplit=1)

            if len(sections) != 2:
                raise ValueError("Markdown was not formatted properly!")

            # Add preceding ordinary text, but avoid empty text nodes.
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.PLAIN, None))

            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))

            text_to_process = sections[1]

        # Add any ordinary text that followed the final image.
        if text_to_process != "":
            new_nodes.append(TextNode(text_to_process, TextType.PLAIN, None))

    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    """
    Split plain-text nodes around Markdown link references.

    Scans each plain-text node for link syntax, replacing each link reference
    with an `LINK` node and preserving surrounding content as `TEXT` nodes.
    Non-text nodes are returned unchanged.

    Args:
        old_nodes: The list of text nodes to process.

    Returns:
        A list of text and link nodes in their original order.
    """
    new_nodes: list[TextNode] = []

    for node in old_nodes:
        # Only plain text nodes can contain markdown link syntax.
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue

        text_to_process: str = node.text

        links: list[tuple[str, str]] = extract_markdown_links(node.text)

        # With no links, preserve the original node unchanged.
        if len(links) == 0:
            new_nodes.append(node)
            continue

        for text, url in links:
            # Split once per the latest link markdown so later links remain in the unprocessed text.
            link_markdown: str = f"[{text}]({url})"
            sections: list[str] = text_to_process.split(link_markdown, maxsplit=1)

            if len(sections) != 2:
                raise ValueError("Markdown was not formatted properly!")

            # Add preceding ordinary text, but avoid empty text nodes.
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.PLAIN, None))

            new_nodes.append(TextNode(text, TextType.LINK, url))

            text_to_process = sections[1]

        # Add any ordinary text that followed the final link.
        if text_to_process != "":
            new_nodes.append(TextNode(text_to_process, TextType.PLAIN, None))

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
