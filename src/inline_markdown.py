import re
from enum import Enum

from htmlnode import HTMLNode
from textnode import TextNode, TextType, text_node_to_html_node


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


def markdown_to_blocks(markdown):
    new_blocks = []
    blocks = markdown.split("\n\n")
    for block in blocks:
        stripped = block.strip()
        if stripped != "":
            new_blocks.append(stripped)
    return new_blocks


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORD_LIST = "unordered_list"
    ORD_LIST = "ordered_list"


def block_to_block_type(block):
    strings = block.split("\n")
    # Header
    if (
        block.startswith("# ")
        or block.startswith("## ")
        or block.startswith("### ")
        or block.startswith("#### ")
        or block.startswith("##### ")
        or block.startswith("###### ")
    ):
        return BlockType.HEADING

    # Code
    if len(strings) > 1:
        first = strings[0].strip()
        last = strings[-1].strip()
        if first.startswith("```") and last.startswith("```"):
            return BlockType.CODE

    # Quote
    is_quote = True
    for s in strings:
        if not s.startswith("> "):
            is_quote = False
            break
    if is_quote:
        return BlockType.QUOTE

    # Unordered
    is_unord = True
    for s in strings:
        if not s.lstrip().startswith("- "):
            is_unord = False
            break
    if is_unord:
        return BlockType.UNORD_LIST

    # Ordered
    num = 1
    is_ord = True
    for s in strings:
        if not s.lstrip().startswith(f"{num}. "):
            is_ord = False
            break
        num += 1
    if is_ord:
        return BlockType.ORD_LIST
    return BlockType.PARAGRAPH


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for node in text_nodes:
        children.append(text_node_to_html_node(node))
    return children


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        blocktype = block_to_block_type(block)

        # Header
        if blocktype == BlockType.HEADING:
            hashcount = 0
            for b in block:
                if b == "#":
                    hashcount += 1
                else:
                    break
            heading_text = block[hashcount:].strip()
            inline_nodes = text_to_children(heading_text)
            header_node = HTMLNode(f"h{hashcount}", children=inline_nodes)
            children.append(header_node)

        # Code
        elif blocktype == BlockType.CODE:
            lines = block.split("\n")
            inner_lines = lines[1:-1]
            stripped_inner = [line.lstrip() for line in inner_lines]
            code_text = "\n".join(stripped_inner) + "\n"
            text_node = TextNode(code_text, TextType.CODE)
            code_child = text_node_to_html_node(text_node)
            pre_node = HTMLNode("pre", children=[code_child])
            children.append(pre_node)

        # Paragraph
        elif blocktype == BlockType.PARAGRAPH:
            paragraph_text = block.replace("\n", " ")
            paragraph_text = " ".join(paragraph_text.split())
            inline_nodes = text_to_children(paragraph_text)
            paragraph_node = HTMLNode("p", children=inline_nodes)
            children.append(paragraph_node)

        # Quote
        elif blocktype == BlockType.QUOTE:
            lines = block.split("\n")
            cleaned_lines = []
            for line in lines:
                line = line.lstrip()
                if line.startswith(">"):
                    cleaned_lines.append(line[1:].lstrip())
            quote_text = " ".join(cleaned_lines)
            inline_nodes = text_to_children(quote_text)
            quote_node = HTMLNode("blockquote", children=inline_nodes)
            children.append(quote_node)

        # Unordered List
        elif blocktype == BlockType.UNORD_LIST:
            lines = block.split("\n")
            li_nodes = []
            for line in lines:
                line = line.lstrip()
                if line.startswith("- "):
                    item_text = line[2:]
                    inline_children = text_to_children(item_text)
                    li_node = HTMLNode("li", children=inline_children)
                    li_nodes.append(li_node)
            unord_node = HTMLNode("ul", children=li_nodes)
            children.append(unord_node)

        # Ordered List
        elif blocktype == BlockType.ORD_LIST:
            lines = block.split("\n")
            li_nodes = []
            num = 1
            for line in lines:
                line = line.lstrip()
                prefix = f"{num}. "
                if line.startswith(prefix):
                    item_text = line[len(prefix) :]
                    inline_children = text_to_children(item_text)
                    li_node = HTMLNode("li", children=inline_children)
                    li_nodes.append(li_node)
                    num += 1
            ord_node = HTMLNode("ol", children=li_nodes)
            children.append(ord_node)

    return HTMLNode("div", children=children)
