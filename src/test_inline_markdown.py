import unittest

from inline_markdown import (
    BlockType,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    extract_title,
    markdown_to_blocks,
    markdown_to_html_node,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)
from textnode import TextNode, TextType


class TestSplitNode(unittest.TestCase):
    def test_split_nodes_delimiter_bold_simple(self):
        node = TextNode("before **bold** after", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        assert len(result) == 3
        assert result[0].text == "before "
        assert result[0].text_type == TextType.TEXT
        assert result[1].text == "bold"
        assert result[1].text_type == TextType.BOLD
        assert result[2].text == " after"
        assert result[2].text_type == TextType.TEXT

    def test_split_nodes_delimiter_italic_double(self):
        node = TextNode("before _italic_ during _moreitalics_ after", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)

        assert len(result) == 5
        assert result[0].text == "before "
        assert result[0].text_type == TextType.TEXT
        assert result[1].text == "italic"
        assert result[1].text_type == TextType.ITALIC
        assert result[2].text == " during "
        assert result[2].text_type == TextType.TEXT
        assert result[3].text == "moreitalics"
        assert result[3].text_type == TextType.ITALIC
        assert result[4].text == " after"
        assert result[4].text_type == TextType.TEXT

    def test_split_nodes_missing_delimiter(self):
        node = TextNode("before plaintext after", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)

        assert len(result) == 1
        assert result[0].text == "before plaintext after"
        assert result[0].text_type == TextType.TEXT

    def test_split_nodes_single_delimiter(self):
        node = TextNode("before `code after", TextType.TEXT)

        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_split_nodes_mixed_delimiters(self):
        nodes = [TextNode("before **bold** after _italics_", TextType.TEXT)]
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)

        assert len(nodes) == 4
        assert nodes[0].text == "before "
        assert nodes[0].text_type == TextType.TEXT
        assert nodes[1].text == "bold"
        assert nodes[1].text_type == TextType.BOLD
        assert nodes[2].text == " after "
        assert nodes[2].text_type == TextType.TEXT
        assert nodes[3].text == "italics"
        assert nodes[3].text_type == TextType.ITALIC

    def test_split_nodes_many_bold(self):
        node = TextNode("before **bold** after **stillbold**", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        assert len(result) == 4
        assert result[0].text == "before "
        assert result[0].text_type == TextType.TEXT
        assert result[1].text == "bold"
        assert result[1].text_type == TextType.BOLD
        assert result[2].text == " after "
        assert result[2].text_type == TextType.TEXT
        assert result[3].text == "stillbold"
        assert result[3].text_type == TextType.BOLD

    def test_split_nodes_starting_delimiters(self):
        node = TextNode("_italics_ are _cool_", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)

        assert len(result) == 3
        assert result[0].text == "italics"
        assert result[0].text_type == TextType.ITALIC
        assert result[1].text == " are "
        assert result[1].text_type == TextType.TEXT
        assert result[2].text == "cool"
        assert result[2].text_type == TextType.ITALIC

    def test_split_nodes_pre_split(self):
        nodes = [
            TextNode("before **bold** after", TextType.TEXT),
            TextNode("already bolded", TextType.BOLD),
        ]
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)

        assert len(nodes) == 4
        assert nodes[0].text == "before "
        assert nodes[0].text_type == TextType.TEXT
        assert nodes[1].text == "bold"
        assert nodes[1].text_type == TextType.BOLD
        assert nodes[2].text == " after"
        assert nodes[2].text_type == TextType.TEXT
        assert nodes[3].text == "already bolded"
        assert nodes[3].text_type == TextType.BOLD

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with an [site](https://boot.dev)"
        )
        self.assertListEqual([("site", "https://boot.dev")], matches)

    def test_extract_markdown_only_images(self):
        matches = extract_markdown_images(
            "This is text with a [site](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_only_links(self):
        matches = extract_markdown_links(
            "This is text with a [site](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("site", "https://boot.dev")], matches)

    def text_extract_markdown_wrong_input(self):
        matches = extract_markdown_links(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link to [bootdev](https://www.boot.dev) and another link to [google](https://www.google.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link to ", TextType.TEXT),
                TextNode("bootdev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and another link to ", TextType.TEXT),
                TextNode("google", TextType.LINK, "https://www.google.com"),
            ],
            new_nodes,
        )

    def test_split_links_missing(self):
        node = TextNode("This is a text that does not have a link", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [TextNode("This is a text that does not have a link", TextType.TEXT)],
            new_nodes,
        )

    def test_split_images_missing(self):
        node = TextNode("This is a text that does not have an image", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [TextNode("This is a text that does not have an image", TextType.TEXT)],
            new_nodes,
        )

    def test_split_links_start(self):
        node = TextNode(
            "[bootdev](https://www.boot.dev) there is a boot.dev link in here somewhere",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("bootdev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" there is a boot.dev link in here somewhere", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_images_only(self):
        node = TextNode("![image](https://i.imgur.com/zjjcJKZ.png)", TextType.IMAGE)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        new_nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes,
        )

    def test_plaintext_to_textnode(self):
        text = "Just some plain text."
        new_nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("Just some plain text.", TextType.TEXT)], new_nodes
        )

    def test_weirdtext_to_textnode(self):
        text = "weird **** case"
        new_nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("weird ", TextType.TEXT),
                TextNode(" case", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_missing_delimiter_to_textnode(self):
        text = "This is **broken"
        with self.assertRaises(ValueError):
            text_to_textnodes(text)

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_paragraph_to_blocks(self):
        md = "Just a single block."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just a single block."])

    def test_markdown_to_blocks_extra_blanks(self):
        md = """
This is **bolded** paragraph


This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line



- This is a list

- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list",
                "- with items",
            ],
        )

    def test_markdown_to_blocks_no_spaces(self):
        md = """
This is **bolded** paragraph
This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line
- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph\nThis is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line\n- This is a list\n- with items"
            ],
        )

    def test_markdown_to_blocks_leading_cases(self):
        md = """

This is **bolded** paragraph
This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items


"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph\nThis is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_paragraph_block(self):
        block = "This is just a normal paragraph."
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_heading_levels(self):
        for i in range(1, 7):
            hashes = "#" * i
            block = f"{hashes} Heading level {i}"
            assert block_to_block_type(block) == BlockType.HEADING

    def test_code_block(self):
        block = "```\nprint('hello')\n```"
        assert block_to_block_type(block) == BlockType.CODE

    def test_not_code_single_line_backticks(self):
        block = "``` not really code ```"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_quote_single_line(self):
        block = "> quoted text"
        assert block_to_block_type(block) == BlockType.QUOTE

    def test_quote_multi_line(self):
        block = "> line one\n> line two\n> line three"
        assert block_to_block_type(block) == BlockType.QUOTE

    def test_quote_invalid_mixed(self):
        block = "> good line\nbad line"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_unordered_list(self):
        block = "- item one\n- item two\n- item three"
        assert block_to_block_type(block) == BlockType.UNORD_LIST

    def test_unordered_list_invalid_mixed(self):
        block = "- item one\nnot a list item"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_ordered_list(self):
        block = "1. first\n2. second\n3. third"
        assert block_to_block_type(block) == BlockType.ORD_LIST

    def test_ordered_list_wrong_start_number(self):
        block = "2. first\n3. second"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_ordered_list_wrong_increment(self):
        block = "1. first\n3. second"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_not_heading_missing_space(self):
        block = "#Not a heading"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_not_unordered_list_missing_space(self):
        block = "-not a list item"
        assert block_to_block_type(block) == BlockType.PARAGRAPH

    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```
    This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_header_unord_list(self):
        md = """
    ## Shopping

    - Apples
    - _Bananas_
    - **Carrots**
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h2>Shopping</h2><ul><li>Apples</li><li><i>Bananas</i></li><li><b>Carrots</b></li></ul></div>",
        )

    def test_mixed_basic(self):
        md = """
    # Title

    This is a _paragraph_ with **bold** and `code`.

    ```
    raw _code_ **here**
    ```
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Title</h1><p>This is a <i>paragraph</i> with <b>bold</b> and <code>code</code>.</p><pre><code>raw _code_ **here**\n</code></pre></div>",
        )

    def test_quote_with_inline(self):
        md = """
    > This is a _fancy_ **quote**
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        assert html == (
            "<div><blockquote>This is a <i>fancy</i> <b>quote</b></blockquote></div>"
        )

    def test_paragraph_and_unordered_list(self):
        md = """
    Shopping list:

    - Apples
    - _Bananas_
    - **Carrots**
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        assert html == (
            "<div>"
            "<p>Shopping list:</p>"
            "<ul>"
            "<li>Apples</li>"
            "<li><i>Bananas</i></li>"
            "<li><b>Carrots</b></li>"
            "</ul>"
            "</div>"
        )

    def test_ordered_md(self):
        md = """
    Steps:

    1. Do _this_
    2. Then **that**
    3. Finally `code`
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        assert html == (
            "<div>"
            "<p>Steps:</p>"
            "<ol>"
            "<li>Do <i>this</i></li>"
            "<li>Then <b>that</b></li>"
            "<li>Finally <code>code</code></li>"
            "</ol>"
            "</div>"
        )

    def test_extract_title(self):
        md = "# Hello"
        result = extract_title(md)
        assert result == "Hello"

    def test_extract_title_multiple(self):
        md = "### Hello"
        with self.assertRaises(Exception):
            extract_title(md)

    def test_extract_title_multi_lines(self):
        md = """
    # Title

    This is a _paragraph_ with **bold** and `code`.

    ```
    raw _code_ **here**
    ```
    """
        result = extract_title(md)
        assert result == "Title"


if __name__ == "__main__":
    unittest.main()
