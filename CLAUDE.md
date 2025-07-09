# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# GUI mode
python main.py

# CLI mode (recommended for development)
python main.py -m sample.md -o output.pptx --silent

# With template
python main.py -m input.md -t template.pptx -o output.pptx --silent

# High-resolution diagrams
python main.py -m input.md -o output.pptx --dpi 300 --silent
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_markdown_parser.py

# Run single test method
pytest tests/test_markdown_parser.py::TestMarkdownParser::test_parse_empty -v

# Run with custom log level
python main.py --log-level DEBUG
```

### Code Quality
```bash
# Format code
black md2pptx

# Type checking (configured in pyproject.toml)
mypy md2pptx

# Linting
flake8 md2pptx
```

### Building
```bash
# Build executable
python build.py

# Build with verbose output
python build.py --verbose
```

## Architecture Overview

### Core Processing Pipeline
The application follows a three-stage pipeline:
1. **Parsing**: Markdown → AST → SlideContent objects
2. **Rendering**: Mermaid diagrams → PNG images (optional)
3. **Building**: SlideContent → PowerPoint file

### Module Structure

#### Parser Module (`md2pptx/parser/`)
- **`markdown_parser.py`**: Uses markdown-it-py to parse Markdown into structured data
- **`models.py`**: Core data structures (`SlideContent`, `MarkdownElement`, `ElementType`)
- Converts Markdown headings to slide boundaries: H1=title slide, H2=new slide, H3=lead text

#### Slides Module (`md2pptx/slides/`)
- **`slide_builder.py`**: Converts parsed content to PowerPoint using python-pptx
- Handles template integration and automatic layout detection
- Supports Lead placeholder (shape name="Lead") for H3 content

#### Diagrams Module (`md2pptx/diagrams/`)
- **`mermaid_renderer.py`**: Renders Mermaid diagrams using headless Chrome (pyppeteer)
- Gracefully degrades when dependencies unavailable
- Uses embedded D3.js from `assets/d3.v7.min.js`

#### GUI Module (`md2pptx/gui/`)
- **`main_window.py`**: CustomTkinter-based interface
- Provides file selection, preview, and progress tracking
- Optional dependency with fallback to CLI-only mode

### Dependency Management
The application uses optional dependencies with graceful degradation:
- Missing Mermaid dependencies → skip diagram rendering
- Missing GUI dependencies → CLI-only mode
- All core functionality (Markdown→PowerPoint) works with minimal dependencies

### Markdown Processing Rules
- **H1** (first only): Title slide
- **H2**: New content slide
- **H3** (immediately after H2): Lead text (requires template with "Lead" shape)
- **Lists**: Converted to PowerPoint bullet points
- **Tables**: Native PowerPoint tables with auto-sizing
- **Code blocks**: Monospace text boxes
- **Images**: Embedded with aspect ratio preservation
- **Mermaid**: Rendered as PNG images when dependencies available

### Template Integration
Templates are loaded via python-pptx with shape name conventions:
- Title placeholder: automatic detection
- Content placeholder: automatic detection  
- Lead placeholder: shape with name="Lead"

### Error Handling
Uses loguru for structured logging with different levels. The application continues processing even when optional features fail (e.g., Mermaid rendering, GUI components).