import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


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

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

        child_node2 = LeafNode(
            "body", "Website", {"href": "https://boot.dev", "target": "_blank"}
        )
        parent_node2 = ParentNode("head", [child_node2])
        self.assertEqual(
            parent_node2.to_html(),
            '<head><body href="https://boot.dev" target="_blank">Website</body></head>',
        )

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_parent_props(self):
        child_node = LeafNode("body", "Website")
        parent_node = ParentNode(
            "head", [child_node], {"href": "https://boot.dev", "target": "_blank"}
        )
        self.assertEqual(
            parent_node.to_html(),
            '<head href="https://boot.dev" target="_blank"><body>Website</body></head>',
        )

    def test_to_html_with_parents_and_child_props(self):
        child_node = ParentNode("span", [LeafNode(None, "hi")], {"class": "inner"})
        parent_node = ParentNode("div", [child_node], {"id": "outer"})
        self.assertEqual(
            parent_node.to_html(), '<div id="outer"><span class="inner">hi</span></div>'
        )

    def test_to_html_tagless_parent(self):
        parent_node = ParentNode(None, [LeafNode("span", "x")])
        with self.assertRaises(ValueError):
            parent_node.to_html()

    def test_to_html_missing_children(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent_node.to_html()

        parent_node2 = ParentNode("div", [])
        with self.assertRaises(ValueError):
            parent_node2.to_html()


if __name__ == "__main__":
    unittest.main()
