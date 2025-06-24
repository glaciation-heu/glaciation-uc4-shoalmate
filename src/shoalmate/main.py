from time import sleep
import logging

from shoalmate.ranker import Ranker


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)


def main() -> None:
    logging.info("Shoalmate started")
    ranker = Ranker()
    while True:
        sleep(10)


if __name__ == "__main__":
    main()
