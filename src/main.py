import sys

from copy_static_files import copy_static_to_docs
from generate_page import generate_pages_recursive


def main():

    basepath: str = sys.argv[1] if len(sys.argv) > 1 else "/"

    copy_static_to_docs()
    generate_pages_recursive(basepath, "content", "template.html", "docs")


if __name__ == "__main__":
    main()
