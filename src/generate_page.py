import os

from block_markdown import extract_title, markdown_to_html_node


def generate_page(
    basepath: str, from_path: str, template_path: str, dest_path: str
) -> None:
    """
    Render a markdown file into a complete HTML page using a template.

    Reads the markdown source and the HTML template, converts the markdown to
    an HTML string via `markdown_to_html_node`, extracts the document title
    via `extract_title`, and substitutes both into the template's
    `{{ Title }}` and `{{ Content }}` placeholders. The filled page is then
    written to `dest_path`, creating any missing parent directories.

    Args:
        basepath: The site's base path (e.g. "/" or "/blog/"). Root-anchored
            `href="/...` and `src="/...` attributes in the template are
            prefixed with this value.
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

    final_template = final_template.replace('href="/', f'href="{basepath}')
    final_template = final_template.replace('src="/', f'src="{basepath}')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "w") as f:
        _ = f.write(final_template)


def generate_pages_recursive(
    basepath: str, content_dir_path: str, template_path: str, dest_dir_path: str
) -> None:
    """
    Render every markdown file in a directory tree into an HTML page.

    Walks `content_dir_path`, mirroring its directory structure into
    `dest_dir_path`. Each `.md` file is rendered via `generate_page` to a
    sibling `.html` path (e.g. `content/blog/post.md` becomes
    `dest_dir_path/blog/post.html`); non-markdown files are ignored.

    Args:
        basepath: The site's base path (e.g. "/" or "/blog/"), passed through
            to `generate_page` for root-anchored `href`/`src` rewriting.
        content_dir_path: Root directory containing the markdown source files.
        template_path: Path to the HTML template file.
        dest_dir_path: Root directory where the generated HTML pages are written.

    Returns:
        None. Rendered pages are written under `dest_dir_path`.
    """
    file_list: list[str] = os.listdir(content_dir_path)
    for file_name in file_list:
        content_file_path: str = os.path.join(content_dir_path, file_name)
        dest_file_path: str = os.path.join(dest_dir_path, file_name)

        if os.path.isfile(content_file_path):
            dest_file_path = dest_file_path[:-3] + ".html"
            generate_page(basepath, content_file_path, template_path, dest_file_path)
        else:
            generate_pages_recursive(
                basepath, content_file_path, template_path, dest_file_path
            )
