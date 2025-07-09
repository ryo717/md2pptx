"""Tests for Markdown parser"""

import pytest
from md2pptx.parser import MarkdownParser
from md2pptx.parser.models import ElementType, SlideContent


class TestMarkdownParser:
    """Test cases for MarkdownParser"""
    
    def setup_method(self):
        """Setup test instance"""
        self.parser = MarkdownParser()
        
    def test_parse_empty(self):
        """Test parsing empty content"""
        slides = self.parser.parse("")
        assert len(slides) == 0
        
    def test_parse_title_slide(self):
        """Test parsing title slide with H1"""
        content = """# Presentation Title

This is the subtitle or introduction."""
        
        slides = self.parser.parse(content)
        assert len(slides) == 1
        assert slides[0].title == "Presentation Title"
        assert slides[0].slide_index == 0
        assert len(slides[0].elements) == 1
        assert slides[0].elements[0].type == ElementType.PARAGRAPH
        
    def test_parse_content_slide(self):
        """Test parsing content slide with H2"""
        content = """# Title

## First Slide

This is content for the first slide."""
        
        slides = self.parser.parse(content)
        assert len(slides) == 2
        assert slides[1].title == "First Slide"
        assert slides[1].slide_index == 1
        
    def test_parse_lead_text(self):
        """Test parsing H3 as lead text"""
        content = """# Title

## Slide with Lead

### This is the lead text

And this is the regular content."""
        
        slides = self.parser.parse(content)
        assert len(slides) == 2
        assert slides[1].lead_text == "This is the lead text"
        
    def test_parse_lists(self):
        """Test parsing lists"""
        content = """# Title

## Lists Example

- Item 1
- Item 2
- Item 3

1. First
2. Second
3. Third"""
        
        slides = self.parser.parse(content)
        assert len(slides) == 2
        
        # Check unordered list
        unordered_list = slides[1].elements[0]
        assert unordered_list.type == ElementType.LIST_UNORDERED
        assert len(unordered_list.children) == 3
        
        # Check ordered list
        ordered_list = slides[1].elements[1]
        assert ordered_list.type == ElementType.LIST_ORDERED
        assert len(ordered_list.children) == 3
        
    def test_parse_code_block(self):
        """Test parsing code blocks"""
        content = """# Title

## Code Example

```python
def hello():
    print("Hello, World!")
```"""
        
        slides = self.parser.parse(content)
        assert len(slides) == 2
        
        code_element = slides[1].elements[0]
        assert code_element.type == ElementType.CODE_BLOCK
        assert "def hello():" in code_element.content
        assert code_element.attributes["language"] == "python"
        
    def test_parse_mermaid(self):
        """Test parsing Mermaid diagrams"""
        content = """# Title

## Diagram

```mermaid
graph TD
    A[Start] --> B[End]
```"""
        
        slides = self.parser.parse(content)
        assert len(slides) == 2
        
        mermaid_element = slides[1].elements[0]
        assert mermaid_element.type == ElementType.MERMAID
        assert "graph TD" in mermaid_element.content
        
    def test_parse_image(self):
        """Test parsing images"""
        content = """# Title

## Image Slide

![Alt text](image.png)"""
        
        slides = self.parser.parse(content)
        assert len(slides) == 2
        
        image_element = slides[1].elements[0]
        assert image_element.type == ElementType.IMAGE
        assert image_element.content == "image.png"
        assert image_element.attributes["alt"] == "Alt text"
        
    def test_parse_table(self):
        """Test parsing tables"""
        content = """# Title

## Table Example

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |"""
        
        slides = self.parser.parse(content)
        assert len(slides) == 2
        
        table_element = slides[1].elements[0]
        assert table_element.type == ElementType.TABLE
        assert table_element.attributes["headers"] == ["Header 1", "Header 2"]
        assert len(table_element.attributes["rows"]) == 2