import unittest

from block_markdown import (
    BlockType,
    block_to_block_type,
    extract_title,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestMarkdownToBlocks(unittest.TestCase):
    # Basic splitting
    def test_single_block(self):
        text = "This is just one block."
        self.assertEqual(markdown_to_blocks(text), ["This is just one block."])

    def test_two_blocks(self):
        text = "# Heading\n\nSome paragraph text."
        self.assertEqual(
            markdown_to_blocks(text),
            ["# Heading", "Some paragraph text."],
        )

    def test_multiple_blocks_in_order(self):
        text = "# Heading\n\nParagraph one.\n\nParagraph two.\n\nParagraph three."
        self.assertEqual(
            markdown_to_blocks(text),
            [
                "# Heading",
                "Paragraph one.",
                "Paragraph two.",
                "Paragraph three.",
            ],
        )

    # Blank line handling
    def test_consecutive_blank_lines_collapse(self):
        text = "First.\n\n\n\n\nSecond."
        self.assertEqual(
            markdown_to_blocks(text),
            ["First.", "Second."],
        )

    def test_blank_lines_are_dropped(self):
        text = "\n\nFirst.\n\n\nSecond.\n\n"
        self.assertEqual(
            markdown_to_blocks(text),
            ["First.", "Second."],
        )

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(markdown_to_blocks(""), [])

    def test_whitespace_only_returns_empty_list(self):
        self.assertEqual(markdown_to_blocks("   \n\n\t\n\n   "), [])

    # Whitespace stripping
    def test_leading_and_trailing_whitespace_stripped(self):
        text = "   padded block   \n\n   another one   "
        self.assertEqual(
            markdown_to_blocks(text),
            ["padded block", "another one"],
        )

    def test_leading_blank_line_is_dropped(self):
        text = "\n\nFirst block.\n\nSecond block."
        self.assertEqual(
            markdown_to_blocks(text),
            ["First block.", "Second block."],
        )

    def test_blank_lines_within_block_preserved(self):
        text = "line one\n\n\nline two"
        self.assertEqual(
            markdown_to_blocks(text),
            ["line one", "line two"],
        )

    # Mixed document
    def test_kitchen_sink_document(self):
        text = (
            "# This is a heading\n\n"
            "This is a paragraph of text with **bold**.\n\n"
            "- first item\n"
            "- second item\n\n"
            "```\ncode block\n```\n\n"
            "> a quote\n\n"
            "final paragraph"
        )
        self.assertEqual(
            markdown_to_blocks(text),
            [
                "# This is a heading",
                "This is a paragraph of text with **bold**.",
                "- first item\n- second item",
                "```\ncode block\n```",
                "> a quote",
                "final paragraph",
            ],
        )


class TestBlockToBlockType(unittest.TestCase):
    # Headings
    def test_h1_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)

    def test_h2_heading(self):
        self.assertEqual(block_to_block_type("## Heading"), BlockType.HEADING)

    def test_h3_heading(self):
        self.assertEqual(block_to_block_type("### Heading"), BlockType.HEADING)

    def test_h4_heading(self):
        self.assertEqual(block_to_block_type("#### Heading"), BlockType.HEADING)

    def test_h5_heading(self):
        self.assertEqual(block_to_block_type("##### Heading"), BlockType.HEADING)

    def test_h6_heading(self):
        self.assertEqual(block_to_block_type("###### Heading"), BlockType.HEADING)

    def test_seven_hashes_is_not_heading(self):
        self.assertEqual(
            block_to_block_type("####### Heading"), BlockType.PARAGRAPH
        )

    def test_hash_without_space_is_not_heading(self):
        self.assertEqual(block_to_block_type("#Heading"), BlockType.PARAGRAPH)

    # Code blocks
    def test_code_block(self):
        code = "```\nprint('hello')\n```"
        self.assertEqual(block_to_block_type(code), BlockType.CODE)

    def test_multiline_code_block(self):
        code = "```\ndef foo():\n    return 42\n```"
        self.assertEqual(block_to_block_type(code), BlockType.CODE)

    def test_unclosed_code_block_is_paragraph(self):
        code = "```\nprint('hello')"
        self.assertEqual(block_to_block_type(code), BlockType.PARAGRAPH)

    def test_opening_fence_without_newline_is_not_code(self):
        code = "```print('hello')```"
        self.assertEqual(block_to_block_type(code), BlockType.PARAGRAPH)

    # Quotes
    def test_single_line_quote(self):
        self.assertEqual(
            block_to_block_type("> This is a quote"), BlockType.QUOTE
        )

    def test_multiline_quote(self):
        quote = "> first line\n> second line\n> third line"
        self.assertEqual(block_to_block_type(quote), BlockType.QUOTE)

    def test_quote_without_space_after_gt(self):
        self.assertEqual(block_to_block_type(">quote"), BlockType.QUOTE)

    def test_mixed_quote_and_text_is_paragraph(self):
        block = "> first line\nnot a quote"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # Unordered lists
    def test_single_item_unordered_list(self):
        self.assertEqual(
            block_to_block_type("- item one"), BlockType.UNORDERED_LIST
        )

    def test_multiline_unordered_list(self):
        block = "- first item\n- second item\n- third item"
        self.assertEqual(
            block_to_block_type(block), BlockType.UNORDERED_LIST
        )

    def test_missing_space_after_dash_is_not_list(self):
        self.assertEqual(block_to_block_type("-item"), BlockType.PARAGRAPH)

    def test_mixed_unordered_list_is_paragraph(self):
        block = "- first item\nsecond item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # Ordered lists
    def test_single_item_ordered_list(self):
        self.assertEqual(
            block_to_block_type("1. item one"), BlockType.ORDERED_LIST
        )

    def test_multiline_ordered_list(self):
        block = "1. first\n2. second\n3. third"
        self.assertEqual(
            block_to_block_type(block), BlockType.ORDERED_LIST
        )

    def test_ordered_list_not_starting_at_one_is_paragraph(self):
        block = "2. second\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_skipping_number_is_paragraph(self):
        block = "1. first\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_missing_space_is_paragraph(self):
        block = "1.first\n2.second"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # Paragraphs
    def test_plain_paragraph(self):
        self.assertEqual(
            block_to_block_type("Just a normal paragraph."),
            BlockType.PARAGRAPH,
        )

    def test_paragraph_with_inline_formatting(self):
        block = "This has **bold** and _italic_ text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):
    # Root wrapping
    def test_empty_document_returns_empty_div(self):
        node = markdown_to_html_node("")
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.to_html(), "<div></div>")

    # Paragraphs
    def test_plain_paragraph(self):
        node = markdown_to_html_node("Just text.")
        self.assertEqual(node.to_html(), "<div><p>Just text.</p></div>")

    def test_paragraph_with_inline_formatting(self):
        node = markdown_to_html_node("a **bold** and _italic_ and `code`")
        self.assertEqual(
            node.to_html(),
            "<div><p>a <b>bold</b> and <i>italic</i> and "
            "<code>code</code></p></div>",
        )

    def test_paragraph_with_link_and_image(self):
        node = markdown_to_html_node("[site](x.dev) ![pic](p.png)")
        self.assertEqual(
            node.to_html(),
            '<div><p><a href="x.dev">site</a> '
            '<img src="p.png" alt="pic"></img></p></div>',
        )

    # Headings
    def test_heading_levels(self):
        node = markdown_to_html_node("### Three")
        self.assertEqual(node.to_html(), "<div><h3>Three</h3></div>")

    def test_heading_with_inline_formatting(self):
        node = markdown_to_html_node("## A **bold** heading")
        self.assertEqual(
            node.to_html(),
            "<div><h2>A <b>bold</b> heading</h2></div>",
        )

    # Code blocks
    def test_code_block(self):
        node = markdown_to_html_node("```\nprint('hi')\n```")
        self.assertEqual(
            node.to_html(),
            "<div><pre><code>print('hi')</code></pre></div>",
        )

    def test_multiline_code_block(self):
        node = markdown_to_html_node("```\ndef foo():\n    return 42\n```")
        self.assertEqual(
            node.to_html(),
            "<div><pre><code>def foo():\n    return 42</code></pre></div>",
        )

    # Quotes
    def test_single_line_quote(self):
        node = markdown_to_html_node("> quoted text")
        self.assertEqual(
            node.to_html(), "<div><blockquote>quoted text</blockquote></div>"
        )

    def test_multiline_quote(self):
        node = markdown_to_html_node("> first line\n> second line")
        self.assertEqual(
            node.to_html(),
            "<div><blockquote>first line\nsecond line</blockquote></div>",
        )

    def test_quote_gt_inside_text_preserved(self):
        node = markdown_to_html_node("> text > more")
        self.assertEqual(
            node.to_html(),
            "<div><blockquote>text > more</blockquote></div>",
        )

    # Unordered lists
    def test_unordered_list(self):
        node = markdown_to_html_node("- first\n- second\n- third")
        self.assertEqual(
            node.to_html(),
            "<div><ul><li>first</li><li>second</li><li>third</li></ul></div>",
        )

    def test_unordered_list_with_inline_formatting(self):
        node = markdown_to_html_node("- **bold** item")
        self.assertEqual(
            node.to_html(),
            "<div><ul><li><b>bold</b> item</li></ul></div>",
        )

    def test_unordered_list_dash_inside_text_preserved(self):
        node = markdown_to_html_node("- item - dash")
        self.assertEqual(
            node.to_html(),
            "<div><ul><li>item - dash</li></ul></div>",
        )

    # Ordered lists
    def test_ordered_list(self):
        node = markdown_to_html_node("1. first\n2. second\n3. third")
        self.assertEqual(
            node.to_html(),
            "<div><ol><li>first</li><li>second</li><li>third</li></ol></div>",
        )

    def test_ordered_list_double_space_after_number(self):
        node = markdown_to_html_node("1.  two spaces")
        self.assertEqual(
            node.to_html(),
            "<div><ol><li>two spaces</li></ol></div>",
        )

    # Mixed document
    def test_mixed_document(self):
        doc = (
            "# Heading\n\n"
            "Paragraph with **bold**.\n\n"
            "```\ncode\n```\n\n"
            "> quote\n\n"
            "- a\n- b\n\n"
            "1. x\n2. y\n\n"
            "final paragraph"
        )
        node = markdown_to_html_node(doc)
        self.assertEqual(
            node.to_html(),
            "<div><h1>Heading</h1>"
            "<p>Paragraph with <b>bold</b>.</p>"
            "<pre><code>code</code></pre>"
            "<blockquote>quote</blockquote>"
            "<ul><li>a</li><li>b</li></ul>"
            "<ol><li>x</li><li>y</li></ol>"
            "<p>final paragraph</p></div>",
        )

    def test_root_is_div(self):
        node = markdown_to_html_node("just text")
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 1)


class TestExtractTitle(unittest.TestCase):
    # Basic extraction
    def test_simple_title(self):
        self.assertEqual(extract_title("# My Title"), "My Title")

    def test_title_with_other_blocks(self):
        markdown = "Some intro paragraph.\n\n# The Real Title\n\nMore text."
        self.assertEqual(extract_title(markdown), "The Real Title")

    def test_title_with_leading_blank_lines(self):
        markdown = "\n\n# Title\n\ntext"
        self.assertEqual(extract_title(markdown), "Title")

    def test_title_with_trailing_whitespace_stripped(self):
        self.assertEqual(extract_title("#   Padded   "), "Padded")

    # Only H1 counts
    def test_lower_level_headings_are_not_titles(self):
        markdown = "## Not a title\n\n# Actual Title"
        self.assertEqual(extract_title(markdown), "Actual Title")

    def test_only_lower_level_headings_raise(self):
        markdown = "## Not a title\n\n### Also not"
        with self.assertRaises(ValueError):
            _ = extract_title(markdown)

    # First H1 wins
    def test_first_h1_wins(self):
        markdown = "# First Title\n\n# Second Title"
        self.assertEqual(extract_title(markdown), "First Title")

    def test_first_h1_after_other_blocks(self):
        markdown = "Intro text.\n\n# Found Title\n\n## Ignored Heading"
        self.assertEqual(extract_title(markdown), "Found Title")

    # Errors
    def test_no_title_raises(self):
        markdown = "Just a paragraph with no heading."
        with self.assertRaises(ValueError):
            _ = extract_title(markdown)

    def test_empty_document_raises(self):
        with self.assertRaises(ValueError):
            _ = extract_title("")


if __name__ == "__main__":
    _ = unittest.main()
