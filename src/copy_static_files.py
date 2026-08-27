import os
import shutil


def copy_files_recursive(src: str, dest: str) -> None:
    """Recursively copy all contents of src into dest.

    Creates dest if it does not exist, then copies every file and
    subdirectory (including nested ones) from src into dest.

    Args:
        src: The source directory to copy from.
        dest: The destination directory to copy into.
    """
    if not os.path.exists(dest):
        os.mkdir(dest)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dest_path = os.path.join(dest, item)

        if os.path.isfile(src_path):
            _ = shutil.copy(src_path, dest_path)
            print(f"Copied: {src_path} -> {dest_path}")
        else:
            copy_files_recursive(src_path, dest_path)


def copy_static_to_docs() -> None:
    """Wipe the docs directory and copy the static directory into it."""
    if os.path.exists("docs"):
        shutil.rmtree("docs")

    copy_files_recursive("static", "docs")
