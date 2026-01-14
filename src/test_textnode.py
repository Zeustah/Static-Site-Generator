import unittest
from enum import Enum

from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD, None)
        node3 = TextNode("This is a text node", TextType.BOLD, "www.google.com")
        node4 = TextNode("This is not a text node", TextType.BOLD)
        node5 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node2, node3)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_image_node_to_html(self):
        node = TextNode("alt text here", TextType.IMAGE, "http://example.com/image.png")
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props["src"], "http://example.com/image.png")
        self.assertEqual(html_node.props["alt"], "alt text here")

    def test_link_node_to_html(self):
        node = TextNode("click me", TextType.LINK, "http://example.com")
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "click me")
        self.assertEqual(html_node.props["href"], "http://example.com")

    def test_bold_node_to_html(self):
        node = TextNode("bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "bold text")
        self.assertIsNone(html_node.props)

    def test_italic_node_to_html(self):
        node = TextNode("italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "italic text")
        self.assertIsNone(html_node.props)

    def test_code_node_to_html(self):
        node = TextNode("code text", TextType.CODE)
        html_node = text_node_to_html_node(node)

        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "code text")
        self.assertIsNone(html_node.props)

    def test_invalid_text_type_raises(self):
        class FakeType(Enum):
            FAKE = "fake"

        node = TextNode("bad", FakeType.FAKE)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)


if __name__ == "__main__":
    unittest.main()
