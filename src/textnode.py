from enum import Enum
from typing import override

from leafnode import LeafNode


class TextType(Enum):
    """
    Enumeration of supported inline text types.

    Each member represents a kind of text segment (e.g., plain, bold, link)
    that can appear in a document.
    """

    PLAIN = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    """
    A node representing a single piece of inline text with a type and optional URL.

    Used to model segments of text in a document, where each segment has a
    specific type (from TextType) and optionally an associated URL for links
    or images.
    """

    def __init__(self, text: str, text_type: TextType, url: str | None = None) -> None:
        """
        Create a text node.

        Args:
            text: The raw text content of the node.
            text_type: The type of text (e.g., plain, bold, link).
            url: Optional URL for link or image nodes.
        """
        self.text: str = text
        self.text_type: TextType = text_type
        self.url: str | None = url

    @override
    def __eq__(self, other: object) -> bool:
        """
        Check structural equality with another object.

        Two TextNode instances are equal if their `text`, `text_type`, and `url`
        attributes are all equal.

        Args:
            other: The object to compare against.

        Returns:
            True if `other` is a TextNode with identical content; otherwise False.
        """
        if not isinstance(other, TextNode):
            return NotImplemented
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )

    @override
    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the node.

        The format mirrors the constructor call, showing the text, type value,
        and optional URL.

        Returns:
            A string like `TextNode('hello', 'plain', None)`.
        """

        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

    def text_node_to_html_node(self, text_node: "TextNode") -> LeafNode:
        """
        Convert a TextNode into its corresponding LeafNode representation.

        Args:
            text_node: The TextNode to convert.

        Returns:
            A LeafNode representing the same content in HTML.

        Raises:
            ValueError: If a LINK or IMAGE TextNode is missing a required URL.
        """
        match text_node.text_type:
            case TextType.PLAIN:
                return LeafNode(None, text_node.text, None)
            case TextType.BOLD:
                return LeafNode("b", text_node.text, None)
            case TextType.ITALIC:
                return LeafNode("i", text_node.text, None)
            case TextType.CODE:
                return LeafNode("code", text_node.text, None)
            case TextType.LINK:
                if text_node.url is None:
                    raise ValueError("Link TextNode requires a URL")
                return LeafNode("a", text_node.text, {"href": text_node.url})
            case TextType.IMAGE:
                if text_node.url is None:
                    raise ValueError("Image TextNode requires a URL")
                return LeafNode(
                    "img", "", {"src": text_node.url, "alt": text_node.text}
                )
