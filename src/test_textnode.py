import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD, None)
        node3 = TextNode("This is a text node", TextType.BOLD, "www.google.com")
        node4 = TextNode("This is not a text node", TextType.BOLD)
        node5 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node2, node3)


if __name__ == "__main__":
    unittest.main()
