import sys

from renderers import CitationRenderer

def main(args):
    for filename in args:
        with CitationRenderer(filename) as renderer:
            renderer.render_file(filename)

if __name__ == "__main__":
    main(sys.argv[1:])
