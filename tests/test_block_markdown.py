import unittest

from block_markdown import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
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


if __name__ == "__main__":
    _ = unittest.main()
