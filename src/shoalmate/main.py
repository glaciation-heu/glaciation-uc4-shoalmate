from time import sleep
import logging

from shoalmate.index_storage import IndexStorage

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)


def main() -> None:
    logging.info("Shoalmate started")
    IndexStorage()
    while True:
        sleep(10)


if __name__ == "__main__":
    main()
