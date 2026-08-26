import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    # Basic splitting
    def test_no_delimiters_returns_single_plain_node(self):
        node = TextNode("no delimiters here", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [TextNode("no delimiters here", TextType.PLAIN)])

    def test_basic_bold_split(self):
        node = TextNode("This is **bold** text", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("This is ", TextType.PLAIN),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.PLAIN),
            ],
        )

    def test_italic_split(self):
        node = TextNode("some *italic* words", TextType.PLAIN)
        result = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(
            result,
            [
                TextNode("some ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" words", TextType.PLAIN),
            ],
        )

    def test_code_split(self):
        node = TextNode("use `printf` here", TextType.PLAIN)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("use ", TextType.PLAIN),
                TextNode("printf", TextType.CODE),
                TextNode(" here", TextType.PLAIN),
            ],
        )

    def test_multiple_segments_in_order(self):
        node = TextNode("**a** b **c** d", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("a", TextType.BOLD),
                TextNode(" b ", TextType.PLAIN),
                TextNode("c", TextType.BOLD),
                TextNode(" d", TextType.PLAIN),
            ],
        )

    def test_converts_all_to_given_type_not_just_first(self):
        node = TextNode("**one** two **three** four **five**", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("one", TextType.BOLD),
                TextNode(" two ", TextType.PLAIN),
                TextNode("three", TextType.BOLD),
                TextNode(" four ", TextType.PLAIN),
                TextNode("five", TextType.BOLD),
            ],
        )

    # Position edge cases
    def test_delimiter_at_start(self):
        node = TextNode("**bold** start", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" start", TextType.PLAIN),
            ],
        )

    def test_delimiter_at_end(self):
        node = TextNode("end **bold**", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("end ", TextType.PLAIN),
                TextNode("bold", TextType.BOLD),
            ],
        )

    def test_entire_string_delimited(self):
        node = TextNode("**all bold**", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [TextNode("all bold", TextType.BOLD)])

    def test_adjacent_empty_delimiters_produce_nothing(self):
        node = TextNode("****", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [])

    def test_empty_string_input(self):
        node = TextNode("", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [])

    def test_whitespace_only_segment_preserved(self):
        node = TextNode("** ** x", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode(" ", TextType.BOLD),
                TextNode(" x", TextType.PLAIN),
            ],
        )

    def test_unicode_content(self):
        node = TextNode("**café 🌍** done", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("café 🌍", TextType.BOLD),
                TextNode(" done", TextType.PLAIN),
            ],
        )

    # Non-plain nodes must pass through untouched (regression: missing `continue`)
    def test_non_plain_node_passthrough_unchanged(self):
        node = TextNode("already code", TextType.CODE)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [TextNode("already code", TextType.CODE)])

    def test_non_plain_node_with_url_passthrough_unchanged(self):
        node = TextNode("click", TextType.LINK, "https://example.com")
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [TextNode("click", TextType.LINK, "https://example.com")],
        )

    def test_non_plain_node_containing_delimiters_not_resplit(self):
        node = TextNode("a **b** c", TextType.CODE)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, [TextNode("a **b** c", TextType.CODE)])

    def test_mixed_list_of_plain_and_non_plain(self):
        nodes = [
            TextNode("plain **bold** text", TextType.PLAIN),
            TextNode("untouched link", TextType.LINK, "https://x.com"),
            TextNode("more *stuff*", TextType.PLAIN),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("plain ", TextType.PLAIN),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.PLAIN),
                TextNode("untouched link", TextType.LINK, "https://x.com"),
                TextNode("more *stuff*", TextType.PLAIN),
            ],
        )

    def test_empty_input_list(self):
        result = split_nodes_delimiter([], "**", TextType.BOLD)
        self.assertEqual(result, [])

    # Error handling: unbalanced delimiters
    def test_unbalanced_delimiters_raise(self):
        node = TextNode("unbalanced ** delim", TextType.PLAIN)
        with self.assertRaises(ValueError):
            _ = split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_only_closing_delimiter_raises(self):
        node = TextNode("text**", TextType.PLAIN)
        with self.assertRaises(ValueError):
            _ = split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_odd_number_of_delimiters_raises(self):
        node = TextNode("**a** b ** c", TextType.PLAIN)
        with self.assertRaises(ValueError):
            _ = split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_unbalanced_error_does_not_swallow_valid_prefix(self):
        # Even a valid-looking prefix must not prevent the error
        node = TextNode("**ok** broken ** pair", TextType.PLAIN)
        with self.assertRaises(ValueError):
            _ = split_nodes_delimiter([node], "**", TextType.BOLD)

    # Multi-character delimiters must match exactly
    def test_double_delimiter_ignored_by_single_char_split(self):
        # "a ** b" split on "*": the empty string between the two asterisks
        # is skipped, so "**" degrades to two adjacent plain segments
        node = TextNode("a ** b", TextType.PLAIN)
        result = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(
            result,
            [
                TextNode("a ", TextType.PLAIN),
                TextNode(" b", TextType.PLAIN),
            ],
        )


class TestExtractMarkdownImages(unittest.TestCase):
    # Basic extraction
    def test_single_image(self):
        text = "![pic](img.png)"
        self.assertEqual(extract_markdown_images(text), [("pic", "img.png")])

    def test_multiple_images_in_order(self):
        text = "![one](1.png) middle ![two](2.png) end ![three](3.png)"
        self.assertEqual(
            extract_markdown_images(text),
            [("one", "1.png"), ("two", "2.png"), ("three", "3.png")],
        )

    def test_image_with_empty_alt_text(self):
        text = "![](logo.png)"
        self.assertEqual(extract_markdown_images(text), [("", "logo.png")])

    def test_image_surrounded_by_other_text(self):
        text = "Look at this ![cat](cat.jpg), pretty cute!"
        self.assertEqual(extract_markdown_images(text), [("cat", "cat.jpg")])

    def test_image_with_complex_url(self):
        text = "![chart](https://cdn.example.com/charts/q3?v=2#revenue)"
        self.assertEqual(
            extract_markdown_images(text),
            [("chart", "https://cdn.example.com/charts/q3?v=2#revenue")],
        )

    # Non-matches must return empty list
    def test_no_images_returns_empty_list(self):
        self.assertEqual(extract_markdown_images("plain text only"), [])

    def test_links_are_not_images(self):
        text = "[boot](boot.dev)"
        self.assertEqual(extract_markdown_images(text), [])

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(extract_markdown_images(""), [])

    # Malformed syntax must not match
    def test_missing_exclamation_is_not_an_image(self):
        text = "this is [alt](img.png) a link, not an image"
        self.assertEqual(extract_markdown_images(text), [])

    def test_unclosed_bracket_does_not_match(self):
        text = "![broken](img.png"
        self.assertEqual(extract_markdown_images(text), [])

    def test_unclosed_parenthesis_does_not_match(self):
        text = "![broken]img.png)"
        self.assertEqual(extract_markdown_images(text), [])

    def test_nested_brackets_in_alt_do_not_match(self):
        text = "![nested [brackets]](img.png)"
        self.assertEqual(extract_markdown_images(text), [])


class TestExtractMarkdownLinks(unittest.TestCase):
    # Basic extraction
    def test_single_link(self):
        text = "[boot](boot.dev)"
        self.assertEqual(extract_markdown_links(text), [("boot", "boot.dev")])

    def test_multiple_links_in_order(self):
        text = "[one](1.dev) middle [two](2.dev) end [three](3.dev)"
        self.assertEqual(
            extract_markdown_links(text),
            [("one", "1.dev"), ("two", "2.dev"), ("three", "3.dev")],
        )

    def test_link_with_empty_anchor_text(self):
        text = "[](boot.dev)"
        self.assertEqual(extract_markdown_links(text), [("", "boot.dev")])

    def test_link_surrounded_by_other_text(self):
        text = "Click [here](page.html) to continue."
        self.assertEqual(extract_markdown_links(text), [("here", "page.html")])

    def test_link_with_complex_url(self):
        text = "[docs](https://docs.example.com/guide?a=1&b=2#intro)"
        self.assertEqual(
            extract_markdown_links(text),
            [("docs", "https://docs.example.com/guide?a=1&b=2#intro")],
        )

    # Non-matches must return empty list
    def test_no_links_returns_empty_list(self):
        self.assertEqual(extract_markdown_links("no links in here"), [])

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(extract_markdown_links(""), [])

    # Image/link distinction (the (?<!!) lookbehind)
    def test_images_are_not_links(self):
        text = "![pic](img.png)"
        self.assertEqual(extract_markdown_links(text), [])

    def test_mixed_images_and_links_extracted_correctly(self):
        text = "![logo](logo.png) and [site](site.dev)"
        self.assertEqual(extract_markdown_links(text), [("site", "site.dev")])
        self.assertEqual(extract_markdown_images(text), [("logo", "logo.png")])

    # Malformed syntax must not match
    def test_unclosed_bracket_does_not_match(self):
        text = "[broken](boot.dev"
        self.assertEqual(extract_markdown_links(text), [])

    def test_unclosed_parenthesis_does_not_match(self):
        text = "[broken]boot.dev)"
        self.assertEqual(extract_markdown_links(text), [])

    def test_nested_brackets_in_anchor_do_not_match(self):
        text = "[nested [text]](boot.dev)"
        self.assertEqual(extract_markdown_links(text), [])

    def test_parens_inside_url_break_the_match(self):
        # URL part forbids parentheses, so this should not fully match
        text = "[wiki](https://en.wikipedia.org/wiki/Python_(programming_language))"
        self.assertNotEqual(
            extract_markdown_links(text),
            [
                (
                    "wiki",
                    "https://en.wikipedia.org/wiki/Python_(programming_language)",
                )
            ],
        )


if __name__ == "__main__":
    _ = unittest.main()
