import unittest

from inline_markdown import split_nodes_delimiter
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


if __name__ == "__main__":
    _ = unittest.main()
