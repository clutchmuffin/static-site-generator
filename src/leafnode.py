from typing import override

from htmlnode import HTMLNode


class LeafNode(HTMLNode):
    """
    An HTML node with no children, representing a single element or text.

    Leaf nodes must have a tag and optionally a text value and attributes.
    They render directly to an HTML string via `to_html`.
    """

    def __init__(
        self,
        tag: str | None,
        value: str,
        props: dict[str, str] | None = None,
    ) -> None:
        """
        Create a leaf HTML node.

        Args:
            tag: The HTML tag name (e.g., "p", "a"). Must not be None.
            value: The text content of the node. Required for leaf nodes.
            props: A mapping of HTML attribute names to their string values.
        """
        super().__init__(tag, value, None, props)

    @override
    def to_html(self) -> str:
        """
        Render this leaf node as an HTML string.

        Returns:
            The HTML representation of this node, e.g. "<p>Text</p>" or "Text"
            if the tag is None.

        Raises:
            ValueError: If `value` is None, since leaf nodes must have content.
        """
        if self.value is None:
            raise ValueError("All leaf nodes must have a value!")

        if self.tag is None:
            return f"{self.value}"

        return f"<{self.tag}{super().props_to_html()}>{self.value}</{self.tag}>"

    @override
    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the node.

        Returns:
            A string like `LeafNode('p', 'text', {'class': 'para'})`.
        """
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
