# mdPage

mdPage is a static site generator written in Python. It takes a folder of
Markdown, renders each page through an HTML template, and drops the finished
site into a `docs/` folder that's ready to publish with GitHub Pages.

## Showcase

This tool was used to build a little Tolkien fan club site, which now lives on
GitHub Pages:

[**Tolkien Fan Club**](https://clutchmuffin.github.io/static-site-generator/)

![JRR Tolkien](static/images/tolkien.png)

It's a good example of what you can put together with it – a homepage, a few
blog posts, and a contact page, all from plain Markdown.

## How it works

The generator is split into a few modules in `src/`:

- **inline_markdown.py** – turns inline Markdown (bold, italics, links, code)
  into nodes.
- **block_markdown.py** – splits a document into blocks (headings, lists,
  quotes, code) and builds an HTML node tree.
- **generate_page.py** – renders each Markdown page through the template.
- **copy_static_files.py** – copies anything in `static/` (CSS, images) into
  the output folder.

Markdown lives in `content/`, the template is `template.html`, and the fields
in that template (`{{ Title }}`, `{{ Content }}`) get filled in during the
build.

## Usage

```sh
./build.sh            # generate the site into docs/
./test.sh             # run the unit tests
```

You can also pass a base path if your site isn't hosted at the root:

```sh
python3 src/main.py "/my/subpath/"
```

The output goes to `docs/`. With GitHub Pages enabled for that folder, a `git
push` is all it takes to publish.

## Tests

The test suite lives in `tests/` and covers the Markdown parsing and page
generation. Run it with:

```sh
./test.sh
```
