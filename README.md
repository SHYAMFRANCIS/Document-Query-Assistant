# Document Query Assistant

AI-powered document analysis and Q&A system built with Streamlit and Google Gemini AI.

## Features

- Upload PDF and DOCX documents
- Ask questions about document content
- AI-powered responses using Google Gemini
- Clean, responsive UI with chat interface
- Secure API key management

## Quick Deploy to Streamlit Cloud

[![Deploy on Streamlit Community Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)

**Deploy in 3 clicks:**
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Select your repo → Add API key in secrets → Deploy!

📖 **Full deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Document-Query-Assistant
```

2. Install dependencies using uv:
```bash
# Using make (recommended)
make install

# Or manually
uv sync
```

3. Configure your Gemini API key (choose one method):

   **Option A: Environment variable**
   ```bash
   # Create .env file from example
   cp .env.example .env
   # Edit .env and add your API key
   ```

   **Option B: Streamlit secrets**
   ```bash
   make setup-secrets
   # Or manually edit .streamlit/secrets.toml
   ```

## Usage

Run the application:
```bash
# Using make (recommended)
make run

# Or manually
uv run streamlit run app.py
```

The app will open at http://localhost:8501

## Development

### Quick Commands

```bash
make help           # Show all available commands
make test           # Run tests
make lint           # Run linter
make lint-fix       # Auto-fix linting errors
make deploy         # Check deployment readiness
make clean          # Clean cache files
```

### Running tests
```bash
uv run pytest
```

### Linting
```bash
uv run ruff check .
```

### Type checking
```bash
uv run mypy .
```

## Project Structure

```
Document-Query-Assistant/
├── app.py                      # Main Streamlit application
├── config/
│   └── settings.py             # Configuration management
├── services/
│   ├── document_parser.py      # PDF/DOCX/TXT parsing
│   └── gemini_service.py       # Gemini AI integration
├── utils/
│   └── session_manager.py      # Session state utilities
├── tests/                      # Test files
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## License

MIT License - see LICENSE file for details.
