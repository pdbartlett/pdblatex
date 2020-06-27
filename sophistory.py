import sys

from renderers import IdiomaticRenderer

def main(args):
    for filename in args:
        with IdiomaticRenderer(filename) as renderer:
            renderer.render_file(filename)

if __name__ == "__main__":
    main(sys.argv[1:])
