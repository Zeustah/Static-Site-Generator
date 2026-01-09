import unittest

from htmlnode import HTMLNode, LeafNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node1 = HTMLNode(
            props={
                "href": "https://www.google.com",
                "target": "_blank",
            },
        )
        node2 = HTMLNode(
            props=None,
        )
        node3 = HTMLNode(props={"href": "https://www.google.com"})

        self.assertEqual(
            node1.props_to_html(),
            ' href="https://www.google.com" target="_blank"',
        )
        self.assertEqual(node2.props_to_html(), "")
        self.assertEqual(node3.props_to_html(), ' href="https://www.google.com"')

    def test_leaf_to_html_p(self):
        node1 = LeafNode("p", "Hello, world!")
        self.assertEqual(node1.to_html(), "<p>Hello, world!</p>")

        node2 = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node2.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )

        node3 = LeafNode(None, "Just text")
        self.assertEqual(node3.to_html(), "Just text")

        node4 = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node4.to_html()

        node5 = LeafNode(
            "a", "Double props", {"href": "https://boot.dev", "target": "_blank"}
        )
        self.assertEqual(
            node5.to_html(),
            '<a href="https://boot.dev" target="_blank">Double props</a>',
        )


if __name__ == "__main__":
    unittest.main()
