"""Main entry point for md2pptx"""

import sys
import argparse
from pathlib import Path
from loguru import logger

from .parser import MarkdownParser
from .slides import SlideBuilder
from .parser.models import ElementType

try:
    from .diagrams import MermaidRenderer
    MERMAID_AVAILABLE = True
except ImportError:
    logger.warning("Mermaid rendering not available")
    MERMAID_AVAILABLE = False
    
try:
    from .gui import MainWindow
    GUI_AVAILABLE = True
except ImportError:
    logger.warning("GUI not available")
    GUI_AVAILABLE = False


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to PowerPoint presentations",
        prog="md2pptx"
    )
    
    parser.add_argument(
        "-m", "--markdown",
        help="Path to Markdown file",
        type=str
    )
    
    parser.add_argument(
        "-t", "--template",
        help="Path to PowerPoint template file",
        type=str
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output PowerPoint file path",
        type=str
    )
    
    parser.add_argument(
        "--silent",
        help="Run in silent mode (no GUI)",
        action="store_true"
    )
    
    parser.add_argument(
        "--dpi",
        help="DPI for rendered diagrams (default: 150)",
        type=int,
        default=150
    )
    
    parser.add_argument(
        "--log-level",
        help="Log level (DEBUG, INFO, WARNING, ERROR)",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO"
    )
    
    return parser.parse_args()


def convert_markdown_to_pptx(markdown_path: str, template_path: str = None, 
                           output_path: str = None, dpi: int = 150) -> str:
    """Convert Markdown file to PowerPoint
    
    Args:
        markdown_path: Path to Markdown file
        template_path: Optional path to template
        output_path: Optional output path
        dpi: DPI for diagrams
        
    Returns:
        Path to created PowerPoint file
    """
    # Default output path
    if not output_path:
        output_path = Path(markdown_path).with_suffix('.pptx')
    
    logger.info(f"Converting {markdown_path} to {output_path}")
    
    # Read markdown
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse markdown
    parser = MarkdownParser()
    slides = parser.parse(content)
    logger.info(f"Parsed {len(slides)} slides")
    
    # Render Mermaid diagrams
    rendered_images = {}
    
    if MERMAID_AVAILABLE:
        mermaid_renderer = MermaidRenderer(dpi=dpi)
        
        for slide in slides:
            for element in slide.elements:
                if element.type == ElementType.MERMAID:
                    logger.info("Rendering Mermaid diagram...")
                    try:
                        image_path = mermaid_renderer.render_sync(element.content)
                        rendered_images[element.content] = image_path
                        logger.info(f"Rendered diagram to {image_path}")
                    except Exception as e:
                        logger.error(f"Failed to render Mermaid: {e}")
    else:
        logger.warning("Skipping Mermaid rendering - dependencies not available")
    
    # Build presentation
    builder = SlideBuilder(template_path)
    
    # Add rendered images
    for mermaid_code, image_path in rendered_images.items():
        builder.add_rendered_image(mermaid_code, image_path)
    
    # Build slides
    builder.build(slides, str(output_path))
    
    logger.info(f"Successfully created: {output_path}")
    return str(output_path)


def main():
    """Main entry point"""
    args = parse_args()
    
    # Configure logger
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=args.log_level
    )
    
    # Check if running in CLI mode
    if args.markdown and (args.silent or args.output):
        # CLI mode
        if not args.markdown:
            logger.error("Markdown file is required in CLI mode")
            sys.exit(1)
            
        try:
            output = convert_markdown_to_pptx(
                args.markdown,
                args.template,
                args.output,
                args.dpi
            )
            print(f"Successfully created: {output}")
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            sys.exit(1)
            
    else:
        # GUI mode
        if not GUI_AVAILABLE:
            logger.error("GUI dependencies not available. Use --silent mode.")
            sys.exit(1)
            
        logger.info("Starting GUI mode")
        app = MainWindow()
        
        # Pre-fill paths if provided
        if args.markdown:
            app.markdown_path.set(args.markdown)
        if args.template:
            app.template_path.set(args.template)
        if args.output:
            app.output_path.set(args.output)
            
        app.run()


if __name__ == "__main__":
    main()