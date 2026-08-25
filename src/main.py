from textnode import TextNode, TextType


def main():
    test_object: TextNode = TextNode(
        "Test Text", TextType.LINK, "https://www.google.com"
    )
    print(test_object)


if __name__ == "__main__":
    main()
