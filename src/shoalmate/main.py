from time import sleep
import logging

from shoalmate.client import read_green_index

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)


def main() -> None:
    logging.info("Shoalmate started")
    read_green_index()
    while True:
        sleep(10)


if __name__ == "__main__":
    main()
