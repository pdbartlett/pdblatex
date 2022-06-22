import logging
import sys

from renderers import IdiomaticRenderer

def main(args):
    logging.basicConfig(filename='sophistory.log', level=logging.DEBUG)
    logging.info("Starting")
    for filename in args:
        with IdiomaticRenderer(filename) as renderer:
            renderer.render_file()
    logging.info("Done")

if __name__ == "__main__":
    main(sys.argv[1:])
