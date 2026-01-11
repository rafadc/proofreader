# Blog Editor

An AI-powered agent that helps review and correct drafts in a Ghost blog, providing intelligent suggestions for typos, structure improvements, and content coherence.

## Overview

This is a command-line application that fetches Ghost blog drafts, analyzes them using LLM-powered agents, generates improvement suggestions, and applies approved changes back to Ghost.

## User Interface (UI/UX)

### Application Flow

1. **Draft Selection Screen**
   - Display all drafts from Ghost blog
   - Sort by most recent first (by updated_at timestamp)
   - User selects a draft to edit

2. **Suggestion Review**
   - Present suggestions one at a time
   - Show before/after comparison with character-level diff highlighting (like git diff)
   - Display explanation/reasoning for each suggestion
   - User can:
     - Approve (y)
     - Reject (n)
     - Edit suggestion in $EDITOR before approving
     - Navigate back/forward with undo/redo capability
     - Quit (q)

3. **Final Confirmation**
   - Show summary of all approved changes
   - Display metrics (time taken, API calls, estimated cost)
   - Require final confirmation before applying to Ghost

4. **Completion**
   - Apply all approved changes to Ghost (batched at end)
   - Show success message with updated draft URL
   - Exit cleanly

### UI Framework: Textual

- Progress indicators showing detailed steps (which node is running)
- Keyboard shortcuts: y=yes, n=no, q=quit
- User-friendly error messages (technical details only in logs)

## Agent Design

The agent is implemented as a LangGraph state machine with sequential node execution:

### Node 1: Style Analysis
- Retrieve last 10-15 published posts (published only, not drafts)
- Extract blog style guidelines using LLM analysis
- Consider target audience and topic (inferred from draft content)
- Cache style analysis for reuse across sessions

### Node 2: Typo Corrections
- Fix spelling and grammar errors only
- No stylistic improvements (strict focus on objective errors)
- Include analysis of image captions, alt text, meta description

### Node 3: Structure Improvements
- Suggest paragraph breaks and section headers
- Propose reordering sections for better flow
- Maintain logical document structure

### Node 4: Coherence & Storytelling
- Check logical flow between ideas
- Verify tone consistency throughout
- Evaluate argument strength and support

### Agent Characteristics

- **Execution**: Sequential (typos → structure → coherence)
- **State Management**: Full draft content stored in LangGraph state
- **LLM Provider**: OpenAI GPT-5.2
- **Suggestions**: Structured objects (Pydantic models/dataclasses)
  - Type (typo/structure/coherence)
  - Location in document
  - Original text
  - Proposed change
  - Reasoning/explanation
- **Style Application**: Include style guidelines in each node's system prompt
- **Content Chunking**: For drafts >10,000 words, split by paragraphs with context overlap
- **Error Handling**: If LLM fails for a node, skip that node and continue
- **Prompt Configuration**: External YAML files for all prompt templates

## Technical Architecture

### Core Stack

- **Language**: Python 3.11+
- **Agent Framework**: LangGraph
- **UI**: Textual
- **LLM**: OpenAI GPT-5.2
- **Linting**: Ruff (strict configuration)
- **Type Checking**: Mypy (strict configuration)
- **Testing**: Pytest (core logic only)
- **Package Manager**: uv
- **Database**: SQLite

### Ghost API Integration

- **Authentication**: Ghost Admin API with key/secret
- **API Version**: Pin to specific version (document requirement)
- **Credentials**: Store in .env file (GHOST_URL, GHOST_API_KEY, GHOST_API_SECRET)
- **Rate Limiting**: Configurable delay between API calls
- **Startup Validation**: Test Ghost connection before showing UI
- **Format Preservation**: Detect and preserve Ghost format (mobiledoc/HTML/markdown) exactly
- **Custom Content**: Preserve unknown custom card types and formatting
- **Conflict Detection**: Check if draft was modified during analysis, warn before applying

### Error Handling & Safety

- **Ghost API Failures**: Retry with exponential backoff, then save locally if all retries fail
- **Startup Errors**: Fail fast with clear error message if API key invalid or Ghost unreachable
- **LLM Failures**: Skip failed node, continue with remaining nodes
- **Safety Checks**: Warn if suggestion deletes more than X% of content
- **Duplicate Detection**: Trust LLM output (no additional duplicate checking)
- **Backup Strategy**: Save original draft JSON to timestamped local file before applying changes

### Data Persistence

#### Database Schema (SQLite)
- Simple flat tables with indexes on frequently queried fields
- **Sessions**: Track editing sessions independently per draft
- **Drafts**: Draft metadata and content snapshots
- **Suggestions**: All generated suggestions with type, location, original, proposed, reasoning
- **Decisions**: User approval/rejection decisions
- **No migrations framework**: Manual schema updates, handle in application code

#### Caching
- Cache style analysis in database for reuse across sessions
- No caching of individual suggestions

#### Export
- Support exporting suggestions and decisions as JSON

### Configuration

- **Environment Variables**: .env file with .env.example in repo showing all variables
- **Config Files**: YAML format for prompt templates
- **Supported Config**:
  - Ghost API credentials and URL
  - Rate limiting delays
  - OpenAI API credentials
  - Logging settings
  - Content deletion warning threshold

### Project Structure

```
blog-editor/
├── src/
│   └── blog_editor/
│       ├── __init__.py
│       ├── main.py                 # CLI entry point
│       ├── config/
│       │   ├── prompts.yaml        # Prompt templates
│       │   └── settings.py         # Config loading
│       ├── ghost/
│       │   ├── client.py           # Ghost API client
│       │   └── models.py           # Ghost data models
│       ├── agent/
│       │   ├── graph.py            # LangGraph definition
│       │   ├── state.py            # Graph state models
│       │   ├── nodes/
│       │   │   ├── style.py        # Style analysis node (function)
│       │   │   ├── typos.py        # Typo correction node (function)
│       │   │   ├── structure.py    # Structure improvement node (function)
│       │   │   └── coherence.py    # Coherence check node (function)
│       │   └── suggestions.py      # Suggestion models
│       ├── ui/
│       │   ├── app.py              # Textual application
│       │   ├── screens/
│       │   │   ├── draft_list.py   # Draft selection screen
│       │   │   └── review.py       # Suggestion review screen
│       │   └── widgets/
│       │       ├── diff.py         # Character-level diff display
│       │       └── progress.py     # Progress indicator
│       └── db/
│           ├── models.py           # SQLAlchemy models
│           └── operations.py       # Database operations
├── tests/
│   ├── fixtures/
│   │   └── ghost_responses.json   # Mock Ghost API responses
│   └── test_*.py                   # Test files
├── .env.example
├── pyproject.toml                  # uv configuration
├── README.md
└── spec.md
```

### CLI Interface

**Entry Point**: `blog-editor`

**Arguments**:
- `--help`: Show help message
- `--dry-run`: Run without applying changes to Ghost

**Example Usage**:
```bash
blog-editor                    # Normal interactive mode
blog-editor --dry-run         # Review mode only
```

### Logging

- **Level**: INFO to file, ERROR to console
- **Location**: Timestamped log files
- **Content**: API calls, agent decisions, errors with technical details
- **Format**: Standard Python logging format

### Metrics & Analytics

- **Tracking**: Time taken, API calls made, estimated cost
- **Display**: Show in final summary screen
- **Telemetry**: None (completely private, no usage tracking)

## Suggestion Processing

### Suggestion Generation

1. Each node generates suggestions as structured Pydantic models
2. Style guidelines included in system prompts
3. Draft audience/topic inferred from content
4. All text analyzed: body, captions, alt text, meta description

### Suggestion Application

1. **Collection**: Batch all approved suggestions until end
2. **Overlapping Edits**: Apply sequentially in order (typos → structure → coherence), updating subsequent suggestions as changes are applied
3. **Manual Edits**: User can open suggestion in $EDITOR to modify before approving
4. **Final Review**: Show all approved changes before applying
5. **Backup**: Save original draft to timestamped JSON file
6. **Ghost Update**: Apply all changes in single API call
7. **Verification**: Check that draft wasn't modified during session (warn if conflict detected)

## Testing Strategy

### Scope
- Core logic: Ghost API client, agent nodes, suggestion generation
- Database operations
- Mock Ghost API responses using fixtures

### Approach
- Pytest for all tests
- Mock Ghost API with fixture data (tests/fixtures/ghost_responses.json)
- Unit tests for individual nodes
- Integration tests for full agent workflow

### Coverage
- Focus on core logic only
- No UI rendering tests
- No comprehensive edge case coverage required

## Development Workflow

### Setup
1. Clone repository
2. Copy .env.example to .env, fill in credentials
3. Install dependencies: `uv sync`
4. Run tests: `pytest`
5. Run application: `blog-editor`

### Code Quality
- **Ruff**: Strict linting on all code
- **Mypy**: Strict type checking, type hints required everywhere
- **Formatting**: Ruff auto-formatting
- **Pre-commit**: Run linting and type checking before commits

### No Development Mode
- Same behavior for development and production
- Use --dry-run flag for testing without Ghost updates

## Documentation

### README.md Contents
- Project overview and purpose
- Installation instructions (uv setup)
- Ghost API setup (creating API keys)
- Configuration (.env variables)
- Usage examples
- Troubleshooting common issues

### .env.example
Include all variables with descriptions:
```
# Ghost Blog Configuration
GHOST_URL=https://yourblog.ghost.io
GHOST_API_KEY=your_admin_api_key
GHOST_API_SECRET=your_admin_api_secret

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Optional Settings
RATE_LIMIT_DELAY=1.0
LOG_LEVEL=INFO
CONTENT_DELETION_WARNING_THRESHOLD=0.2
```

## Key Design Decisions Summary

### Authentication & Configuration
- Ghost Admin API with key/secret in .env
- YAML for config files (prompts)
- Pin to specific Ghost API version

### Agent Behavior
- Sequential node execution (not parallel)
- OpenAI GPT-4/4o as LLM provider
- Cache style analysis, regenerate suggestions fresh
- Include all metadata in analysis
- Process long drafts in paragraph-based chunks

### UI/UX
- One suggestion at a time with undo/redo
- Character-level diff highlighting
- Always show reasoning for suggestions
- Keyboard shortcuts (y/n/q)
- Progress indicators with detailed steps

### Data Management
- Batch updates at end (not incremental)
- SQLite with simple schema, basic indexes
- Track separate sessions per draft
- Export to JSON format
- Backup original before applying changes

### Safety & Reliability
- Retry Ghost API calls, then save locally
- Detect conflicts if draft modified during analysis
- Warn on large content deletions
- Validate Ghost connection on startup
- User-friendly errors, technical details in logs

### Implementation Simplicity
- Functions for LangGraph nodes (not classes)
- Minimal CLI arguments
- No filtering/skipping of suggestion types
- No development mode
- Manual database schema updates
- Trust LLM for duplicate detection
- Single user, one draft at a time

## Non-Goals

- Multi-user support or concurrent sessions
- Automatic publishing of drafts
- Integration with other blogging platforms
- Real-time collaborative editing
- Advanced analytics or reporting
- Custom plugin system
- Web-based UI
- Mobile application
