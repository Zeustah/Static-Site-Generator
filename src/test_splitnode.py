import unittest

from splitnode import split_nodes_delimiter
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


if __name__ == "__main__":
    unittest.main()
