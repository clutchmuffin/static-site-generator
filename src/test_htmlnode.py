import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    # Basic instantiation tests
    def test_init_minimal(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_init_with_tag(self):
        node = HTMLNode(tag="div")
        self.assertEqual(node.tag, "div")

    def test_init_with_value(self):
        node = HTMLNode(value="text")
        self.assertEqual(node.value, "text")

    def test_init_with_children(self):
        child = HTMLNode(tag="span")
        node = HTMLNode(tag="div", children=[child])
        self.assertEqual(node.children, [child])

    def test_init_with_props(self):
        props = {"class": "btn", "id": "main"}
        node = HTMLNode(tag="button", props=props)
        self.assertEqual(node.props, props)

    # props_to_html tests
    def test_props_to_html_no_props(self):
        node = HTMLNode(tag="div")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_empty_dict(self):
        node = HTMLNode(tag="div", props={})
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_single_prop(self):
        node = HTMLNode(tag="div", props={"class": "container"})
        self.assertEqual(node.props_to_html(), ' class="container"')

    def test_props_to_html_multiple_props(self):
        node = HTMLNode(
            tag="input",
            props={"type": "text", "name": "username", "value": "Alice"},
        )
        # Order is insertion order: type, name, value
        self.assertEqual(
            node.props_to_html(),
            ' type="text" name="username" value="Alice"',
        )

    def test_props_to_html_special_characters_in_value(self):
        node = HTMLNode(tag="a", props={"href": "https://example.com?a=1&b=2"})
        # No HTML escaping is done by props_to_html
        self.assertEqual(
            node.props_to_html(),
            ' href="https://example.com?a=1&b=2"',
        )

    def test_props_to_html_with_quotes_in_value(self):
        node = HTMLNode(tag="div", props={"data-info": 'say "hello"'})
        # Implementation does NOT escape quotes; it just embeds them
        self.assertEqual(
            node.props_to_html(),
            ' data-info="say "hello""',
        )

    def test_props_to_html_with_empty_string_value(self):
        node = HTMLNode(tag="input", props={"value": ""})
        self.assertEqual(node.props_to_html(), ' value=""')

    def test_props_to_html_with_space_in_value(self):
        node = HTMLNode(tag="div", props={"class": "btn primary"})
        self.assertEqual(node.props_to_html(), ' class="btn primary"')

    def test_props_order_preserved(self):
        props = {"z": "1", "a": "2", "m": "3"}
        node = HTMLNode(tag="div", props=props)
        # Insertion order: z, a, m
        self.assertEqual(
            node.props_to_html(),
            ' z="1" a="2" m="3"',
        )

    # repr tests
    def test_repr_basic(self):
        node = HTMLNode()
        self.assertEqual(
            repr(node),
            "HTMLNode(None, None, None, None)",
        )

    def test_repr_with_tag_and_value(self):
        node = HTMLNode(tag="p", value="text")
        self.assertEqual(
            repr(node),
            "HTMLNode(p, text, None, None)",
        )

    def test_repr_with_children(self):
        child = HTMLNode(tag="span")
        node = HTMLNode(tag="div", children=[child])
        self.assertEqual(
            repr(node),
            "HTMLNode(div, None, [HTMLNode(span, None, None, None)], None)",
        )

    def test_repr_with_props(self):
        node = HTMLNode(tag="img", props={"src": "x.png", "alt": "img"})
        self.assertEqual(
            repr(node),
            "HTMLNode(img, None, None, {'src': 'x.png', 'alt': 'img'})",
        )

    def test_repr_with_newline_in_value(self):
        node = HTMLNode(tag="pre", value="line1\nline2")
        # Note: newline is literal in the output, not escaped
        self.assertEqual(
            repr(node),
            "HTMLNode(pre, line1\nline2, None, None)",
        )

    # to_html NotImplementedError test
    def test_to_html_not_implemented(self):
        node = HTMLNode(tag="div")
        with self.assertRaises(NotImplementedError):
            _ = node.to_html()

    # Edge cases and additional checks
    def test_children_can_be_nested(self):
        grandchild = HTMLNode(tag="span", value="text")
        child = HTMLNode(tag="li", children=[grandchild])
        node = HTMLNode(tag="ul", children=[child])
        assert node.children is not None
        assert node.children[0].children is not None
        self.assertEqual(node.children[0].children[0].value, "text")


if __name__ == "__main__":
    _ = unittest.main()
