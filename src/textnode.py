from enum import Enum
from typing import override


class TextType(Enum):
    PLAIN = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
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
