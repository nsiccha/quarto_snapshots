"""Console script for quarto_snapshots."""
import quarto_snapshots as qs
if __name__ == "__main__":
    sys.exit(qs.handle_args(qs.get_parser().parse_args()))  # pragma: no cover
