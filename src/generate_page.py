import os

from block_markdown import extract_title, markdown_to_html_node


def generate_page(from_path: str, template_path: str, dest_path: str) -> None:
    """
    Render a markdown file into a complete HTML page using a template.

    Reads the markdown source and the HTML template, converts the markdown to
    an HTML string via `markdown_to_html_node`, extracts the document title
    via `extract_title`, and substitutes both into the template's
    `{{ Title }}` and `{{ Content }}` placeholders. The filled page is then
    written to `dest_path`, creating any missing parent directories.

    Args:
        from_path: Path to the markdown source file.
        template_path: Path to the HTML template file.
        dest_path: Path where the generated HTML page should be written.

    Returns:
        None. The rendered page is written to `dest_path`.
    """

    print(f"Generating page from '{from_path}' to '{dest_path}' using {template_path}")

    with open(from_path, "r") as f:
        markdown: str = f.read()

    with open(template_path, "r") as f:
        template: str = f.read()

    markdown_html_string: str = markdown_to_html_node(markdown).to_html()
    markdown_title: str = extract_title(markdown)

    new_title_template: str = template.replace("{{ Title }}", markdown_title)
    final_template: str = new_title_template.replace(
        "{{ Content }}", markdown_html_string
    )

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "w") as f:
        _ = f.write(final_template)
