import unittest

from block_markdown import markdown_to_blocks


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


if __name__ == "__main__":
    _ = unittest.main()
