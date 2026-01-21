import os
import shutil
import sys

from htmlnode import HTMLNode
from inline_markdown import extract_title, markdown_to_html_node


def copy_files_recursive(src, dst):
    if not os.path.exists(dst):
        os.mkdir(dst)
    for filename in os.listdir(src):
        src_path = os.path.join(src, filename)
        dst_path = os.path.join(dst, filename)
        print(f" * {src_path} -> {dst_path}")
        if os.path.isfile(src_path):
            shutil.copy(src_path, dst_path)
        else:
            copy_files_recursive(src_path, dst_path)


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page {from_path} to {dest_path} from {template_path}...")
    with open(from_path, "r") as file:
        markdown = file.read()
    with open(template_path, "r") as file:
        template = file.read()
    md_node = markdown_to_html_node(markdown)
    md_html = md_node.to_html()
    title = extract_title(markdown)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", md_html)
    template = template.replace('href="/', f'href="{basepath}')
    template = template.replace('src="/', f'src="{basepath}')
    with open(dest_path, "w") as f:
        f.write(template)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for filename in os.listdir(dir_path_content):
        file_path = os.path.join(dir_path_content, filename)
        dest_path = os.path.join(dest_dir_path, filename)
        if os.path.isfile(file_path):
            if file_path.endswith(".md"):
                dest_path = dest_path.replace(".md", ".html")
                generate_page(file_path, template_path, dest_path, basepath)
        else:
            os.makedirs(dest_path)
            generate_pages_recursive(file_path, template_path, dest_path, basepath)


def main():
    if len(sys.argv) >= 2:
        basepath = sys.argv[1]
    else:
        basepath = "/"

    base_dir = os.path.dirname(os.path.dirname(__file__))
    docs_path = os.path.join(base_dir, "docs")
    static_path = os.path.join(base_dir, "static")
    content_path = os.path.join(base_dir, "content")
    template_path = os.path.join(base_dir, "template.html")

    if os.path.exists(docs_path):
        shutil.rmtree(docs_path)
    copy_files_recursive(static_path, docs_path)
    print("Generating new 'public' directory.")
    generate_pages_recursive(content_path, template_path, docs_path, basepath)


if __name__ == "__main__":
    main()
