import re

from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            parts = node.text.split(delimiter)
            if len(parts) % 2 == 0:
                raise ValueError("invalid markdown, missing closing delimiter")
            for i, part in enumerate(parts):
                if part == "":
                    continue
                if i % 2 != 0:
                    node_type = text_type
                else:
                    node_type = TextType.TEXT
                new_node = TextNode(part, node_type)
                new_nodes.append(new_node)
    return new_nodes


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        node_images = extract_markdown_images(node.text)
        if not node_images:
            new_nodes.append(node)
            continue
        current_text = node.text
        for img, link in node_images:
            before, after = current_text.split(f"![{img}]({link})", 1)
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(img, TextType.IMAGE, link))
            current_text = after
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        node_links = extract_markdown_links(node.text)
        if not node_links:
            new_nodes.append(node)
            continue
        current_text = node.text
        for alt, url in node_links:
            before, after = current_text.split(f"[{alt}]({url})", 1)
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.LINK, url))
            current_text = after
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    return new_nodes


def text_to_textnodes(text):
    new_text = [TextNode(text, TextType.TEXT)]
    new_text = split_nodes_delimiter(new_text, "**", TextType.BOLD)
    new_text = split_nodes_delimiter(new_text, "_", TextType.ITALIC)
    new_text = split_nodes_delimiter(new_text, "`", TextType.CODE)
    new_text = split_nodes_link(new_text)
    new_text = split_nodes_image(new_text)
    return new_text
