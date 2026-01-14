from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            parts = node.text.split(delimiter)
            if len(parts) % 2 == 0:
                raise Exception("invalid markdown, missing closing delimiter")
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
