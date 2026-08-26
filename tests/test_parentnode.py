import unittest

from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode


class TestParentNode(unittest.TestCase):
    # Basic instantiation tests
    def test_init_minimal(self):
        child = LeafNode(tag="span", value="text")
        node = ParentNode(tag="div", children=[child])
        self.assertEqual(node.tag, "div")
        self.assertIsNone(node.value)
        self.assertEqual(node.children, [child])
        self.assertIsNone(node.props)

    def test_init_with_props(self):
        child = LeafNode(tag="li", value="item")
        props = {"class": "list", "id": "main"}
        node = ParentNode(tag="ul", children=[child], props=props)
        self.assertEqual(node.props, props)

    def test_init_with_multiple_children(self):
        c1 = LeafNode(tag="b", value="bold")
        c2 = LeafNode(tag="i", value="italic")
        node = ParentNode(tag="p", children=[c1, c2])
        self.assertEqual(node.children, [c1, c2])

    # to_html tests: basic cases
    def test_to_html_single_child(self):
        child = LeafNode(tag="span", value="Hello")
        node = ParentNode(tag="div", children=[child])
        self.assertEqual(node.to_html(), "<div><span>Hello</span></div>")

    def test_to_html_multiple_children(self):
        c1 = LeafNode(tag="b", value="bold")
        c2 = LeafNode(tag="i", value="italic")
        node = ParentNode(tag="p", children=[c1, c2])
        self.assertEqual(
            node.to_html(),
            "<p><b>bold</b><i>italic</i></p>",
        )

    def test_to_html_with_props(self):
        child = LeafNode(tag="span", value="x")
        node = ParentNode(
            tag="div",
            children=[child],
            props={"class": "container", "id": "main"},
        )
        # Props order: insertion order (class, id)
        self.assertEqual(
            node.to_html(),
            '<div class="container" id="main"><span>x</span></div>',
        )

    def test_to_html_nested_parent_nodes(self):
        inner = ParentNode(
            tag="li",
            children=[LeafNode(tag="span", value="item")],
        )
        outer = ParentNode(
            tag="ul",
            children=[inner],
            props={"class": "list"},
        )
        self.assertEqual(
            outer.to_html(),
            '<ul class="list"><li><span>item</span></li></ul>',
        )

    def test_to_html_mixed_leaf_and_parent_children(self):
        leaf = LeafNode(tag="b", value="bold")
        parent = ParentNode(
            tag="span",
            children=[LeafNode(tag="i", value="italic")],
        )
        node = ParentNode(tag="div", children=[leaf, parent])
        self.assertEqual(
            node.to_html(),
            "<div><b>bold</b><span><i>italic</i></span></div>",
        )

    # to_html tests: error cases
    def test_to_html_raises_when_tag_is_none(self):
        child = LeafNode(tag="span", value="text")
        node = ParentNode(tag="div", children=[child])
        node.tag = None  # force None to test the branch
        with self.assertRaises(ValueError):
            _ = node.to_html()

    def test_to_html_raises_when_children_is_none(self):
        node = ParentNode(tag="div", children=[LeafNode(tag="span", value="x")])
        node.children = None  # force None to test the branch
        with self.assertRaises(ValueError):
            _ = node.to_html()

    # to_html tests: edge cases
    def test_to_html_empty_children_list(self):
        # Logically odd, but allowed by current constructor signature
        node = ParentNode(tag="div", children=[])
        self.assertEqual(node.to_html(), "<div></div>")

    def test_to_html_child_with_empty_value(self):
        child = LeafNode(tag="span", value="")
        node = ParentNode(tag="div", children=[child])
        self.assertEqual(node.to_html(), "<div><span></span></div>")

    def test_to_html_child_with_newlines(self):
        child = LeafNode(tag="pre", value="line1\nline2")
        node = ParentNode(tag="div", children=[child])
        self.assertEqual(
            node.to_html(),
            "<div><pre>line1\nline2</pre></div>",
        )

    def test_to_html_child_with_angle_brackets(self):
        # No HTML escaping is done
        child = LeafNode(tag="code", value="<b>bold</b>")
        node = ParentNode(tag="div", children=[child])
        self.assertEqual(
            node.to_html(),
            "<div><code><b>bold</b></code></div>",
        )

    def test_to_html_props_with_special_characters(self):
        child = LeafNode(tag="span", value="x")
        node = ParentNode(
            tag="a",
            children=[child],
            props={"href": "https://example.com?a=1&b=2"},
        )
        self.assertEqual(
            node.to_html(),
            '<a href="https://example.com?a=1&b=2"><span>x</span></a>',
        )

    def test_to_html_props_with_quotes_in_value(self):
        # Implementation does not escape quotes
        child = LeafNode(tag="span", value="x")
        node = ParentNode(
            tag="div",
            children=[child],
            props={"data-info": 'say "hello"'},
        )
        self.assertEqual(
            node.to_html(),
            '<div data-info="say "hello""><span>x</span></div>',
        )

    # repr tests
    def test_repr_basic(self):
        child = LeafNode(tag="span", value="text")
        node = ParentNode(tag="div", children=[child])
        self.assertEqual(
            repr(node),
            "ParentNode(div, [LeafNode(span, text, None)], None)",
        )

    def test_repr_with_props(self):
        child = LeafNode(tag="span", value="x")
        node = ParentNode(
            tag="div",
            children=[child],
            props={"class": "container"},
        )
        self.assertEqual(
            repr(node),
            "ParentNode(div, [LeafNode(span, x, None)], {'class': 'container'})",
        )

    def test_repr_with_multiple_children(self):
        c1 = LeafNode(tag="b", value="bold")
        c2 = LeafNode(tag="i", value="italic")
        node = ParentNode(tag="p", children=[c1, c2])
        self.assertEqual(
            repr(node),
            "ParentNode(p, [LeafNode(b, bold, None), LeafNode(i, italic, None)], None)",
        )

    # Inheritance and type checks
    def test_instance_of_htmlnode(self):
        child = LeafNode(tag="span", value="text")
        node = ParentNode(tag="div", children=[child])
        self.assertIsInstance(node, HTMLNode)

    # Complex nesting scenarios
    def test_to_html_deep_nesting(self):
        # div > ul > li > span > text
        leaf = LeafNode(tag="span", value="item")
        li = ParentNode(tag="li", children=[leaf])
        ul = ParentNode(tag="ul", children=[li])
        div = ParentNode(tag="div", children=[ul], props={"class": "wrap"})

        self.assertEqual(
            div.to_html(),
            '<div class="wrap"><ul><li><span>item</span></li></ul></div>',
        )

    def test_to_html_multiple_siblings_and_nested(self):
        # div > [p>b, ul>li*2]
        b = LeafNode(tag="b", value="bold")
        p = ParentNode(tag="p", children=[b])

        li1 = ParentNode(tag="li", children=[LeafNode(tag="span", value="one")])
        li2 = ParentNode(tag="li", children=[LeafNode(tag="span", value="two")])
        ul = ParentNode(tag="ul", children=[li1, li2])

        div = ParentNode(tag="div", children=[p, ul])

        self.assertEqual(
            div.to_html(),
            "<div><p><b>bold</b></p><ul><li><span>one</span></li><li><span>two</span></li></ul></div>",
        )


if __name__ == "__main__":
    _ = unittest.main()
