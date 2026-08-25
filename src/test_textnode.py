import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    # Basic equality tests
    def test_eq_same_plain(self):
        node = TextNode("This is a text node", TextType.PLAIN)
        node2 = TextNode("This is a text node", TextType.PLAIN)
        self.assertEqual(node, node2)

    def test_eq_same_bold(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_same_with_url(self):
        node = TextNode("click here", TextType.LINK, "https://example.com")
        node2 = TextNode("click here", TextType.LINK, "https://example.com")
        self.assertEqual(node, node2)

    def test_eq_same_with_none_url_explicit(self):
        node = TextNode("text", TextType.CODE, None)
        node2 = TextNode("text", TextType.CODE, None)
        self.assertEqual(node, node2)

    # Inequality tests
    def test_ne_different_text(self):
        node = TextNode("text A", TextType.BOLD)
        node2 = TextNode("text B", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_ne_different_type(self):
        node = TextNode("text", TextType.BOLD)
        node2 = TextNode("text", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_ne_different_url(self):
        node = TextNode("text", TextType.LINK, "https://a.com")
        node2 = TextNode("text", TextType.LINK, "https://b.com")
        self.assertNotEqual(node, node2)

    def test_ne_url_vs_none_url(self):
        node = TextNode("text", TextType.LINK, "https://a.com")
        node2 = TextNode("text", TextType.LINK, None)
        self.assertNotEqual(node, node2)

    # Edge cases
    def test_eq_empty_string(self):
        node = TextNode("", TextType.PLAIN)
        node2 = TextNode("", TextType.PLAIN)
        self.assertEqual(node, node2)

    def test_eq_whitespace_strings(self):
        node = TextNode("   ", TextType.PLAIN)
        node2 = TextNode("   ", TextType.PLAIN)
        self.assertEqual(node, node2)

    def test_ne_whitespace_difference(self):
        node = TextNode("text", TextType.PLAIN)
        node2 = TextNode("text ", TextType.PLAIN)
        self.assertNotEqual(node, node2)

    def test_eq_unicode_and_emoji(self):
        node = TextNode("hello 🌍", TextType.BOLD)
        node2 = TextNode("hello 🌍", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_ne_unicode_difference(self):
        node = TextNode("café", TextType.PLAIN)
        node2 = TextNode("cafe", TextType.PLAIN)
        self.assertNotEqual(node, node2)

    def test_eq_case_sensitive(self):
        node = TextNode("Text", TextType.PLAIN)
        node2 = TextNode("Text", TextType.PLAIN)
        self.assertEqual(node, node2)

    def test_ne_case_difference(self):
        node = TextNode("Text", TextType.PLAIN)
        node2 = TextNode("text", TextType.PLAIN)
        self.assertNotEqual(node, node2)

    def test_eq_all_text_types(self):
        for t in TextType:
            node = TextNode("x", t, None)
            node2 = TextNode("x", t, None)
            self.assertEqual(node, node2, msg=f"Failed for TextType.{t.name}")

    def test_eq_image_type_with_url(self):
        node = TextNode("alt", TextType.IMAGE, "https://img.png")
        node2 = TextNode("alt", TextType.IMAGE, "https://img.png")
        self.assertEqual(node, node2)

    # Comparison with non-TextNode
    def test_eq_with_non_textnode(self):
        node = TextNode("text", TextType.PLAIN)
        self.assertNotEqual(node, "text")
        self.assertNotEqual(node, 123)
        self.assertNotEqual(node, None)
        self.assertNotEqual(node, {"text": "text"})

    # Reflexivity, symmetry, transitivity sanity checks
    def test_eq_reflexive(self):
        node = TextNode("reflexive", TextType.CODE, "https://x.com")
        self.assertEqual(node, node)

    def test_eq_symmetric(self):
        a = TextNode("sym", TextType.BOLD, "https://s.com")
        b = TextNode("sym", TextType.BOLD, "https://s.com")
        self.assertEqual(a, b)
        self.assertEqual(b, a)

    def test_eq_transitive(self):
        a = TextNode("trans", TextType.ITALIC)
        b = TextNode("trans", TextType.ITALIC)
        c = TextNode("trans", TextType.ITALIC)
        self.assertEqual(a, b)
        self.assertEqual(b, c)
        self.assertEqual(a, c)


if __name__ == "__main__":
    _ = unittest.main()
