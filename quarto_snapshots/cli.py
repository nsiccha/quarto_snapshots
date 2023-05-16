"""Console script for quarto_snapshots."""
import argparse
import sys


def main():
    """Console script for quarto_snapshots."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "quarto_snapshots.cli.main")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
