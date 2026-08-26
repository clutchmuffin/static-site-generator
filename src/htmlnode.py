from typing import override


class HTMLNode:
    """
    A node in an HTML tree representing a single element or text segment.

    Subclasses should implement `to_html` to define how the node is rendered
    as an HTML string. This base class provides common attributes for tags,
    text content, child nodes, and HTML attributes.
    """

    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: list["HTMLNode"] | None = None,
        props: dict[str, str] | None = None,
    ) -> None:
        """
        Create an HTML node.

        Args:
            tag: The HTML tag name (e.g., "div", "p"). None for text-only nodes.
            value: The text content of the node. Used when the node has no children.
            children: A list of child HTMLNode instances.
            props: A mapping of HTML attribute names to their string values.
        """
        self.tag: str | None = tag
        self.value: str | None = value
        self.children: list[HTMLNode] | None = children
        self.props: dict[str, str] | None = props

    def to_html(self) -> str:
        """
        Render this node and its children as an HTML string.

        Subclasses must implement this method to define how the node is converted
        to HTML.

        Returns:
            The HTML representation of this node.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    def props_to_html(self) -> str:
        """
        Render the node's attributes as an HTML attribute string.

        Returns:
            A string like ` class="btn" id="main"` (note the leading space),
            or an empty string if there are no props.
        """
        if self.props is None:
            return ""

        result = ""
        for key, val in self.props.items():
            result += f' {key}="{val}"'
        return result

    @override
    def __repr__(self) -> str:
        """
        Return a developer-friendly string representation of the node.

        Returns:
            A string like `HTMLNode('div', None, [...], {'class': 'container'})`.
        """
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
