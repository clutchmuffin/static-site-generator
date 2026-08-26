from typing import override

from htmlnode import HTMLNode


class ParentNode(HTMLNode):
    """
    An HTML node with children, representing a container element.

    Parent nodes must have a tag and a non-empty list of child nodes.
    They render their children recursively via `to_html`.
    """

    def __init__(
        self,
        tag: str,
        children: list["HTMLNode"],
        props: dict[str, str] | None = None,
    ) -> None:
        """
        Create a parent HTML node.

        Args:
            tag: The HTML tag name (e.g., "div", "ul"). Must not be None.
            children: A list of child HTMLNode instances.
            props: A mapping of HTML attribute names to their string values.
        """
        super().__init__(tag, None, children, props)

    @override
    def to_html(self) -> str:
        """
        Render this parent node and all descendants as an HTML string.

        Returns:
            The HTML representation of this node, including all children.

        Raises:
            ValueError: If `tag` is None or `children` is None.
        """
        if self.tag is None:
            raise ValueError("ParentNode cannot exist without a tag")
        if self.children is None:
            raise ValueError("ParentNode cannot exist without children")

        result = ""
        for child in self.children:
            result += child.to_html()

        return f"<{self.tag}{super().props_to_html()}>{result}</{self.tag}>"

    @override
    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the node.

        Returns:
            A string like `ParentNode(div, [...], {'class': 'container'})`.
        """
        return f"ParentNode({self.tag}, {self.children}, {self.props})"
