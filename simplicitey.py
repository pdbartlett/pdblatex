import sys

from renderers import CitationRenderer, render

def main(args):
    for filename in args:
        with CitationRenderer(filename) as renderer:
            render(filename, renderer)

if __name__ == "__main__":
    main(sys.argv[1:])
