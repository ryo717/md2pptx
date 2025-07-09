"""Mermaid diagram renderer using Pyppeteer and D3.js"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import base64
from loguru import logger
try:
    from pyppeteer import launch
    PYPPETEER_AVAILABLE = True
except ImportError:
    PYPPETEER_AVAILABLE = False
    logger.warning("pyppeteer not available - Mermaid rendering disabled")
    
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False
    logger.warning("cairosvg not available - SVG conversion disabled")
    
from PIL import Image
import io


class MermaidRenderer:
    """Render Mermaid diagrams to PNG images"""
    
    def __init__(self, dpi: int = 150):
        """Initialize the Mermaid renderer
        
        Args:
            dpi: DPI for output images
        """
        self.dpi = dpi
        self.browser = None
        self.page = None
        
        # Path to bundled D3.js
        self.d3_path = Path(__file__).parent.parent / "assets" / "d3.v7.min.js"
        if not self.d3_path.exists():
            logger.warning(f"D3.js not found at {self.d3_path}")
            
        logger.info(f"Mermaid renderer initialized with DPI={dpi}")
        
    async def _initialize_browser(self):
        """Initialize headless browser"""
        if not PYPPETEER_AVAILABLE:
            raise RuntimeError("pyppeteer not available")
            
        if not self.browser:
            self.browser = await launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.page = await self.browser.newPage()
            await self.page.setViewport({'width': 1920, 'height': 1080})
            logger.info("Headless browser initialized")
            
    async def render(self, mermaid_code: str, output_path: Optional[str] = None) -> str:
        """Render Mermaid code to PNG
        
        Args:
            mermaid_code: Mermaid diagram code
            output_path: Optional output file path
            
        Returns:
            Path to the rendered PNG file
        """
        try:
            # Initialize browser if needed
            await self._initialize_browser()
            
            # Create HTML with embedded Mermaid
            html_content = self._create_html(mermaid_code)
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                html_path = f.name
                
            try:
                # Load the HTML
                await self.page.goto(f'file://{html_path}')
                
                # Wait for rendering
                await self.page.waitForSelector('#diagram svg', timeout=10000)
                
                # Get the SVG content
                svg_content = await self.page.evaluate('''() => {
                    const svg = document.querySelector('#diagram svg');
                    return svg ? svg.outerHTML : null;
                }''')
                
                if not svg_content:
                    raise ValueError("Failed to render Mermaid diagram")
                
                # Convert SVG to PNG
                if not output_path:
                    output_path = tempfile.mktemp(suffix='.png')
                    
                self._svg_to_png(svg_content, output_path)
                
                logger.info(f"Rendered Mermaid diagram to {output_path}")
                return output_path
                
            finally:
                # Clean up temporary HTML
                os.unlink(html_path)
                
        except Exception as e:
            logger.error(f"Failed to render Mermaid diagram: {e}")
            raise
            
    def _create_html(self, mermaid_code: str) -> str:
        """Create HTML page with Mermaid diagram"""
        
        # Read D3.js content if available
        d3_script = ""
        if self.d3_path.exists():
            d3_script = f'<script>{self.d3_path.read_text()}</script>'
        else:
            # Fallback to CDN (for development only)
            d3_script = '<script src="https://d3js.org/d3.v7.min.js"></script>'
            
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    {d3_script}
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; background: white; }}
        #diagram {{ display: inline-block; }}
    </style>
</head>
<body>
    <div id="diagram" class="mermaid">
{mermaid_code}
    </div>
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: false,
                htmlLabels: true
            }}
        }});
    </script>
</body>
</html>
'''
        return html
        
    def _svg_to_png(self, svg_content: str, output_path: str):
        """Convert SVG to PNG"""
        if not CAIROSVG_AVAILABLE:
            raise RuntimeError("cairosvg not available")
            
        # Convert SVG to PNG using cairosvg
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            dpi=self.dpi
        )
        
        # Open with PIL to ensure proper format
        image = Image.open(io.BytesIO(png_data))
        
        # Save as PNG
        image.save(output_path, 'PNG', dpi=(self.dpi, self.dpi))
        
    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
            logger.info("Browser closed")
            
    def render_sync(self, mermaid_code: str, output_path: Optional[str] = None) -> str:
        """Synchronous wrapper for render method"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.render(mermaid_code, output_path))
        finally:
            loop.run_until_complete(self.close())
            loop.close()