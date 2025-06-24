import logging

from shoalmate.orchestrator import Orchestrator


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)


def main() -> None:
    logging.info("Shoalmate started")
    Orchestrator().run()


if __name__ == "__main__":
    main()
