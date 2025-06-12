from time import sleep
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)


def main():
    logging.info("Shoalmate started!")
    while True:
        sleep(10)


if __name__ == "__main__":
    main()
