import argparse
from proofreader.ui.app import ProofreaderApp

def main():
    parser = argparse.ArgumentParser(description="Proofreader - AI powered Ghost draft reviewer")
    parser.add_argument("--dry-run", action="store_true", help="Run without applying changes to Ghost")
    args = parser.parse_args()

    app = ProofreaderApp(dry_run=args.dry_run)
    app.run()

if __name__ == "__main__":
    main()
