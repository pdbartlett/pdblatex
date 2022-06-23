import logging
import sys

from renderers import LaTeXExtrasRenderer

def main(args):
    logging.basicConfig(filename='sophistory.log', level=logging.DEBUG)
    logging.info("Starting")
    for filename in args:
        with LaTeXExtrasRenderer(filename) as renderer:
            renderer.render_file()
    logging.info("Done")

if __name__ == "__main__":
    main(sys.argv[1:])
