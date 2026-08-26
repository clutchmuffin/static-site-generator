def markdown_to_blocks(markdown: str) -> list[str]:
    """Split a markdown document into blocks separated by blank lines.

    Blocks are separated by one or more blank lines. Each returned block is
    stripped of surrounding whitespace, and empty blocks are dropped.

    Args:
        markdown: The raw markdown document as a string.

    Returns:
        A list of non-empty, whitespace-stripped markdown blocks.
    """
    lines: list[str] = markdown.split("\n\n")
    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            continue
        new_lines.append(stripped)
    return new_lines
