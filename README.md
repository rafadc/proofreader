# Blog Editor

An AI-powered agent that helps review and correct drafts in a Ghost blog, providing intelligent suggestions for typos, structure improvements, and content coherence.

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    uv sync
    ```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Set the following variables in `.env`:
- `GHOST_URL`: Your Ghost blog URL
- `GHOST_API_KEY`: Your Ghost Admin API Key
- `GHOST_API_SECRET`: Your Ghost Admin API Secret (if applicable, typically part of the key)
- `OPENAI_API_KEY`: Your OpenAI API Key

## Usage

To run the application:

```bash
uv run blog-editor
```

To run in review-only mode (no changes applied to Ghost):

```bash
uv run blog-editor --dry-run
```
