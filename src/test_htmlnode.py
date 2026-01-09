import unittest

from htmlnode import HTMLNode


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


if __name__ == "__main__":
    unittest.main()
