import unittest

from htmlnode import HTMLNode
from leafnode import LeafNode


class TestLeafNode(unittest.TestCase):
    # Basic instantiation tests
    def test_init_minimal(self):
        node = LeafNode(tag="p", value="text")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "text")
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_init_with_props(self):
        props = {"class": "btn", "id": "main"}
        node = LeafNode(tag="button", value="Click", props=props)
        self.assertEqual(node.props, props)

    # to_html tests: basic cases
    def test_to_html_simple_tag_with_value(self):
        node = LeafNode(tag="p", value="Hello")
        self.assertEqual(node.to_html(), "<p>Hello</p>")

    def test_to_html_with_single_prop(self):
        node = LeafNode(tag="p", value="Hello", props={"class": "intro"})
        self.assertEqual(node.to_html(), '<p class="intro">Hello</p>')

    def test_to_html_with_multiple_props(self):
        node = LeafNode(
            tag="input",
            value="",
            props={"type": "text", "name": "username"},
        )
        # Order is insertion order: type, name
        self.assertEqual(
            node.to_html(),
            '<input type="text" name="username"></input>',
        )

    def test_to_html_tag_none_returns_value_only(self):
        # Technically LeafNode requires tag: str, but value-only case is covered
        # by the logic: if tag is None, return value.
        # We'll test via a subclass or by temporarily setting tag to None.
        node = LeafNode(tag="p", value="Just text")
        node.tag = None  # force None to test the branch
        self.assertEqual(node.to_html(), "Just text")

    # to_html tests: error cases
    def test_to_html_raises_when_value_is_none(self):
        node = LeafNode(tag="p", value=None)
        with self.assertRaises(ValueError):
            _ = node.to_html()

    # to_html tests: edge cases in values and props
    def test_to_html_empty_value(self):
        node = LeafNode(tag="span", value="")
        self.assertEqual(node.to_html(), "<span></span>")

    def test_to_html_value_with_spaces(self):
        node = LeafNode(tag="div", value="  spaced  ")
        self.assertEqual(node.to_html(), "<div>  spaced  </div>")

    def test_to_html_value_with_newlines(self):
        node = LeafNode(tag="pre", value="line1\nline2")
        self.assertEqual(node.to_html(), "<pre>line1\nline2</pre>")

    def test_to_html_value_with_angle_brackets(self):
        # No HTML escaping is done by this implementation
        node = LeafNode(tag="code", value="<b>bold</b>")
        self.assertEqual(node.to_html(), "<code><b>bold</b></code>")

    def test_to_html_prop_with_special_characters(self):
        node = LeafNode(
            tag="a",
            value="link",
            props={"href": "https://example.com?a=1&b=2"},
        )
        self.assertEqual(
            node.to_html(),
            '<a href="https://example.com?a=1&b=2">link</a>',
        )

    def test_to_html_prop_with_quotes_in_value(self):
        # Implementation does not escape quotes
        node = LeafNode(
            tag="div",
            value="x",
            props={"data-info": 'say "hello"'},
        )
        self.assertEqual(
            node.to_html(),
            '<div data-info="say "hello"">x</div>',
        )

    # repr tests
    def test_repr_basic(self):
        node = LeafNode(tag="p", value="text")
        self.assertEqual(repr(node), "LeafNode(p, text, None)")

    def test_repr_with_props(self):
        node = LeafNode(
            tag="img",
            value="alt text",
            props={"src": "x.png", "alt": "img"},
        )
        self.assertEqual(
            repr(node),
            "LeafNode(img, alt text, {'src': 'x.png', 'alt': 'img'})",
        )

    def test_repr_with_none_value(self):
        node = LeafNode(tag="br", value=None)
        self.assertEqual(repr(node), "LeafNode(br, None, None)")

    # Inheritance checks
    def test_instance_of_htmlnode(self):
        node = LeafNode(tag="p", value="text")
        self.assertIsInstance(node, HTMLNode)


if __name__ == "__main__":
    _ = unittest.main()
