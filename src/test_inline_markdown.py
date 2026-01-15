import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
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


if __name__ == "__main__":
    unittest.main()
