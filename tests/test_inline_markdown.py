import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
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


class TestSplitNodesImage(unittest.TestCase):
    # Basic splitting
    def test_single_image_in_middle(self):
        node = TextNode("hello ![cat](cat.png) world", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("hello ", TextType.PLAIN),
                TextNode("cat", TextType.IMAGE, "cat.png"),
                TextNode(" world", TextType.PLAIN),
            ],
        )

    def test_image_at_start(self):
        node = TextNode("![cat](cat.png) and rest", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("cat", TextType.IMAGE, "cat.png"),
                TextNode(" and rest", TextType.PLAIN),
            ],
        )

    def test_image_at_end(self):
        node = TextNode("before ![cat](cat.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("before ", TextType.PLAIN),
                TextNode("cat", TextType.IMAGE, "cat.png"),
            ],
        )

    def test_entire_string_is_image(self):
        node = TextNode("![cat](cat.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(result, [TextNode("cat", TextType.IMAGE, "cat.png")])

    def test_multiple_images_in_order(self):
        node = TextNode("![a](1.png) x ![b](2.png) y ![c](3.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("a", TextType.IMAGE, "1.png"),
                TextNode(" x ", TextType.PLAIN),
                TextNode("b", TextType.IMAGE, "2.png"),
                TextNode(" y ", TextType.PLAIN),
                TextNode("c", TextType.IMAGE, "3.png"),
            ],
        )

    def test_adjacent_images(self):
        node = TextNode("![a](1.png)![b](2.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("a", TextType.IMAGE, "1.png"),
                TextNode("b", TextType.IMAGE, "2.png"),
            ],
        )

    def test_image_with_empty_alt(self):
        node = TextNode("![](pic.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(result, [TextNode("", TextType.IMAGE, "pic.png")])

    def test_image_with_unicode_alt(self):
        node = TextNode("![café 🌍](pic.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(result, [TextNode("café 🌍", TextType.IMAGE, "pic.png")])

    def test_image_with_complex_url(self):
        node = TextNode(
            "![chart](https://cdn.example.com/charts/q3?v=2#top)", TextType.PLAIN
        )
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode(
                    "chart", TextType.IMAGE, "https://cdn.example.com/charts/q3?v=2#top"
                )
            ],
        )

    # Passthrough cases
    def test_no_images_preserves_plain_node(self):
        node = TextNode("just some text with [a link](x.dev)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(result, [node])

    def test_empty_input_list(self):
        self.assertEqual(split_nodes_image([]), [])

    def test_non_plain_nodes_pass_through_unchanged(self):
        node = TextNode("already bold", TextType.BOLD)
        result = split_nodes_image([node])
        self.assertEqual(result, [node])

    def test_non_plain_node_with_url_pass_through_unchanged(self):
        node = TextNode("click", TextType.LINK, "https://example.com")
        result = split_nodes_image([node])
        self.assertEqual(result, [node])

    def test_mixed_plain_and_non_plain_nodes(self):
        nodes = [
            TextNode("pic: ![cat](cat.png)", TextType.PLAIN),
            TextNode("keep me", TextType.CODE),
            TextNode("another ![dog](dog.png)", TextType.PLAIN),
        ]
        result = split_nodes_image(nodes)
        self.assertEqual(
            result,
            [
                TextNode("pic: ", TextType.PLAIN),
                TextNode("cat", TextType.IMAGE, "cat.png"),
                TextNode("keep me", TextType.CODE),
                TextNode("another ", TextType.PLAIN),
                TextNode("dog", TextType.IMAGE, "dog.png"),
            ],
        )

    def test_links_are_not_split_as_images(self):
        node = TextNode("see [here](x.dev) and ![pic](p.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("see [here](x.dev) and ", TextType.PLAIN),
                TextNode("pic", TextType.IMAGE, "p.png"),
            ],
        )

    def test_no_extra_empty_plain_nodes(self):
        node = TextNode("![a](1.png) ![b](2.png)", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(
            result,
            [
                TextNode("a", TextType.IMAGE, "1.png"),
                TextNode(" ", TextType.PLAIN),
                TextNode("b", TextType.IMAGE, "2.png"),
            ],
        )


class TestSplitNodesLink(unittest.TestCase):
    # Basic splitting
    def test_single_link_in_middle(self):
        node = TextNode("click [here](x.dev) now", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("click ", TextType.PLAIN),
                TextNode("here", TextType.LINK, "x.dev"),
                TextNode(" now", TextType.PLAIN),
            ],
        )

    def test_link_at_start(self):
        node = TextNode("[here](x.dev) and rest", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("here", TextType.LINK, "x.dev"),
                TextNode(" and rest", TextType.PLAIN),
            ],
        )

    def test_link_at_end(self):
        node = TextNode("before [here](x.dev)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("before ", TextType.PLAIN),
                TextNode("here", TextType.LINK, "x.dev"),
            ],
        )

    def test_entire_string_is_link(self):
        node = TextNode("[here](x.dev)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(result, [TextNode("here", TextType.LINK, "x.dev")])

    def test_multiple_links_in_order(self):
        node = TextNode("[a](1.dev) x [b](2.dev) y [c](3.dev)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("a", TextType.LINK, "1.dev"),
                TextNode(" x ", TextType.PLAIN),
                TextNode("b", TextType.LINK, "2.dev"),
                TextNode(" y ", TextType.PLAIN),
                TextNode("c", TextType.LINK, "3.dev"),
            ],
        )

    def test_adjacent_links(self):
        node = TextNode("[a](1.dev)[b](2.dev)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("a", TextType.LINK, "1.dev"),
                TextNode("b", TextType.LINK, "2.dev"),
            ],
        )

    def test_link_with_empty_anchor(self):
        node = TextNode("[](boot.dev)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(result, [TextNode("", TextType.LINK, "boot.dev")])

    def test_link_with_unicode_anchor(self):
        node = TextNode("[café 🌍](x.dev)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(result, [TextNode("café 🌍", TextType.LINK, "x.dev")])

    def test_link_with_complex_url(self):
        node = TextNode(
            "[docs](https://docs.example.com/guide?a=1&b=2#intro)", TextType.PLAIN
        )
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode(
                    "docs", TextType.LINK, "https://docs.example.com/guide?a=1&b=2#intro"
                )
            ],
        )

    # Passthrough cases
    def test_no_links_preserves_plain_node(self):
        node = TextNode("just text with no links at all", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_empty_string_node_preserved(self):
        node = TextNode("", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_empty_input_list(self):
        self.assertEqual(split_nodes_link([]), [])

    def test_non_plain_nodes_pass_through_unchanged(self):
        node = TextNode("already code", TextType.CODE)
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_non_plain_node_with_url_pass_through_unchanged(self):
        node = TextNode("alt", TextType.IMAGE, "img.png")
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_mixed_plain_and_non_plain_nodes(self):
        nodes = [
            TextNode("go [there](x.dev) now", TextType.PLAIN),
            TextNode("keep me", TextType.BOLD),
            TextNode("and [back](y.dev)", TextType.PLAIN),
        ]
        result = split_nodes_link(nodes)
        self.assertEqual(
            result,
            [
                TextNode("go ", TextType.PLAIN),
                TextNode("there", TextType.LINK, "x.dev"),
                TextNode(" now", TextType.PLAIN),
                TextNode("keep me", TextType.BOLD),
                TextNode("and ", TextType.PLAIN),
                TextNode("back", TextType.LINK, "y.dev"),
            ],
        )

    def test_images_are_not_split_as_links(self):
        # Image syntax stays literal plain text since (?<!!) excludes it
        node = TextNode("![pic](p.png) then [here](x.dev)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode("![pic](p.png) then ", TextType.PLAIN),
                TextNode("here", TextType.LINK, "x.dev"),
            ],
        )

    def test_whitespace_only_segment_preserved(self):
        node = TextNode(" [here](x.dev)", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(
            result,
            [
                TextNode(" ", TextType.PLAIN),
                TextNode("here", TextType.LINK, "x.dev"),
            ],
        )


class TestTextToTextnodes(unittest.TestCase):
    # Basic cases
    def test_plain_text_only(self):
        result = text_to_textnodes("just some text")
        self.assertEqual(result, [TextNode("just some text", TextType.PLAIN)])

    def test_empty_string(self):
        # Empty segments are dropped by the delimiter passes
        result = text_to_textnodes("")
        self.assertEqual(result, [])

    # Single delimiters
    def test_single_bold(self):
        result = text_to_textnodes("**bold**")
        self.assertEqual(result, [TextNode("bold", TextType.BOLD)])

    def test_single_italic(self):
        result = text_to_textnodes("_italic_")
        self.assertEqual(result, [TextNode("italic", TextType.ITALIC)])

    def test_single_code(self):
        result = text_to_textnodes("`code`")
        self.assertEqual(result, [TextNode("code", TextType.CODE)])

    def test_bold_in_sentence(self):
        result = text_to_textnodes("This is **bold** text")
        self.assertEqual(
            result,
            [
                TextNode("This is ", TextType.PLAIN),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.PLAIN),
            ],
        )

    # Mixed inline formatting
    def test_bold_italic_code_mixed(self):
        result = text_to_textnodes("**bold** and _italic_ and `code`")
        self.assertEqual(
            result,
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and ", TextType.PLAIN),
                TextNode("code", TextType.CODE),
            ],
        )

    def test_bold_pair_not_mangled_by_italic_split(self):
        # Bold must be handled before italic so "**" isn't read as empty italics
        result = text_to_textnodes("**b**")
        self.assertEqual(result, [TextNode("b", TextType.BOLD)])

    def test_nested_plain_segments_preserved(self):
        result = text_to_textnodes("a **b** c _d_ e")
        self.assertEqual(
            result,
            [
                TextNode("a ", TextType.PLAIN),
                TextNode("b", TextType.BOLD),
                TextNode(" c ", TextType.PLAIN),
                TextNode("d", TextType.ITALIC),
                TextNode(" e", TextType.PLAIN),
            ],
        )

    # Images and links
    def test_image(self):
        result = text_to_textnodes("![alt text](img.png)")
        self.assertEqual(
            result, [TextNode("alt text", TextType.IMAGE, "img.png")]
        )

    def test_link(self):
        result = text_to_textnodes("[boot](boot.dev)")
        self.assertEqual(
            result, [TextNode("boot", TextType.LINK, "boot.dev")]
        )

    def test_image_and_link_in_one_string(self):
        result = text_to_textnodes("![pic](p.png) and [here](x.dev)")
        self.assertEqual(
            result,
            [
                TextNode("pic", TextType.IMAGE, "p.png"),
                TextNode(" and ", TextType.PLAIN),
                TextNode("here", TextType.LINK, "x.dev"),
            ],
        )

    # Kitchen sink
    def test_full_pipeline(self):
        result = text_to_textnodes(
            "Hello **bold** world with _italic_ and `code`, "
            "plus a [link](x.dev) and ![img](i.png)"
        )
        self.assertEqual(
            result,
            [
                TextNode("Hello ", TextType.PLAIN),
                TextNode("bold", TextType.BOLD),
                TextNode(" world with ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and ", TextType.PLAIN),
                TextNode("code", TextType.CODE),
                TextNode(", plus a ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "x.dev"),
                TextNode(" and ", TextType.PLAIN),
                TextNode("img", TextType.IMAGE, "i.png"),
            ],
        )

    def test_link_brackets_not_treated_as_delimiters(self):
        # Link/image splitting runs before delimiter splitting
        result = text_to_textnodes("[x](y.dev) **b**")
        self.assertEqual(
            result,
            [
                TextNode("x", TextType.LINK, "y.dev"),
                TextNode(" ", TextType.PLAIN),
                TextNode("b", TextType.BOLD),
            ],
        )

    # Underscores are the italic delimiter
    def test_underscore_delimiter_in_sentence(self):
        result = text_to_textnodes("this is _italic_ text")
        self.assertEqual(
            result,
            [
                TextNode("this is ", TextType.PLAIN),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.PLAIN),
            ],
        )

    def test_underscore_in_url_is_literal(self):
        # Link/URL underscores are safe because links are split before
        # the italic delimiter pass and pass through as LINK nodes
        result = text_to_textnodes("see [my_var](https://x.dev/foo_bar)")
        self.assertEqual(
            result,
            [
                TextNode("see ", TextType.PLAIN),
                TextNode("my_var", TextType.LINK, "https://x.dev/foo_bar"),
            ],
        )

    def test_odd_underscores_in_plain_text_raise(self):
        # snake_case has a single underscore, an unmatched italic delimiter
        with self.assertRaises(ValueError):
            _ = text_to_textnodes("use snake_case names")

    # Errors
    def test_unbalanced_bold_raises(self):
        with self.assertRaises(ValueError):
            _ = text_to_textnodes("unbalanced **bold")

    def test_unbalanced_code_raises(self):
        with self.assertRaises(ValueError):
            _ = text_to_textnodes("broken `code")


if __name__ == "__main__":
    _ = unittest.main()
