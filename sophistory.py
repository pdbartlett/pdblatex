import sys

from renderers import IdiomaticRenderer, render

def main(args):
    for filename in args:
        with IdiomaticRenderer(filename) as renderer:
            render(filename, renderer)

if __name__ == "__main__":
    main(sys.argv[1:])
