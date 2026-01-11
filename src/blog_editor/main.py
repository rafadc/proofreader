import argparse
from blog_editor.ui.app import BlogEditorApp

def main():
    parser = argparse.ArgumentParser(description="Blog Editor - AI powered Ghost draft reviewer")
    parser.add_argument("--dry-run", action="store_true", help="Run without applying changes to Ghost")
    args = parser.parse_args()

    app = BlogEditorApp(dry_run=args.dry_run)
    app.run()

if __name__ == "__main__":
    main()
