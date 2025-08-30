#!/usr/bin/env python3


from pprint import pprint
from markdown_it import MarkdownIt


def main():
    md = MarkdownIt()

    md_string = "This is a [text](https://google.com/)"

    parsed = md.parse(md_string)

    #pprint(parsed[0])

    for token in md.parse(md_string):
        #print(token)

        if token.children is not None:
            for child in token.children:
                if token.type == "link_open":
                    child.attrSet("class", "asd")


    print(md.get_all_rules())
    #print(md.render(parsed))

main()
