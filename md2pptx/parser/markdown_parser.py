"""Markdown parser implementation using markdown-it-py"""

import re
from typing import List, Dict, Any, Optional, Tuple
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from loguru import logger

from .models import MarkdownElement, SlideContent, ElementType


class MarkdownParser:
    """Parse Markdown content into structured slide data"""
    
    def __init__(self):
        """Initialize the Markdown parser"""
        self.md = MarkdownIt("commonmark", {"breaks": True, "html": True})
        self.md.enable(["table", "strikethrough"])
        logger.info("Markdown parser initialized")
        
    def parse(self, markdown_content: str) -> List[SlideContent]:
        """Parse Markdown content into slides
        
        Args:
            markdown_content: The Markdown text to parse
            
        Returns:
            List of SlideContent objects
        """
        logger.info("Starting Markdown parsing")
        
        # Parse to syntax tree
        tokens = self.md.parse(markdown_content)
        tree = SyntaxTreeNode(tokens)
        
        # Process the tree into slides
        slides = self._process_tree(tree, markdown_content)
        
        logger.info(f"Parsed {len(slides)} slides")
        return slides
        
    def _process_tree(self, tree: SyntaxTreeNode, original_content: str) -> List[SlideContent]:
        """Process the syntax tree into slides"""
        slides = []
        current_slide = None
        h1_found = False
        
        for node in tree.children:
            if node.type == "heading":
                level = node.tag[1]  # h1, h2, h3 -> 1, 2, 3
                
                if level == "1" and not h1_found:
                    # First H1 becomes title slide
                    h1_found = True
                    current_slide = SlideContent(
                        title=self._get_text_content(node),
                        slide_index=0
                    )
                    # Collect content until next heading for notes
                    notes_content = self._collect_until_heading(node, original_content)
                    current_slide.set_notes(notes_content)
                    
                elif level == "2":
                    # H2 starts a new slide
                    if current_slide:
                        slides.append(current_slide)
                    
                    current_slide = SlideContent(
                        title=self._get_text_content(node),
                        slide_index=len(slides) + 1
                    )
                    
                    # Check for H3 lead text immediately after
                    next_node = self._get_next_sibling(node)
                    if next_node and next_node.type == "heading" and next_node.tag == "h3":
                        current_slide.lead_text = self._get_text_content(next_node)
                    
                    # Collect section content for notes
                    section_content = self._collect_section_content(node, original_content)
                    current_slide.set_notes(section_content)
                    
                elif level == "3" and current_slide:
                    # H3 after H2 is already handled as lead text
                    pass
                    
            elif current_slide:
                # Add content to current slide
                element = self._node_to_element(node)
                if element:
                    current_slide.add_element(element)
        
        # Add the last slide
        if current_slide:
            slides.append(current_slide)
            
        return slides
        
    def _node_to_element(self, node: SyntaxTreeNode) -> Optional[MarkdownElement]:
        """Convert a syntax tree node to a MarkdownElement"""
        
        if node.type == "paragraph":
            # Check for images or mermaid blocks
            text = self._get_text_content(node)
            
            # Check for mermaid diagram
            if "```mermaid" in text:
                mermaid_content = self._extract_mermaid(text)
                if mermaid_content:
                    return MarkdownElement(
                        type=ElementType.MERMAID,
                        content=mermaid_content
                    )
            
            # Check for images
            img_match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', text)
            if img_match:
                return MarkdownElement(
                    type=ElementType.IMAGE,
                    content=img_match.group(2),
                    attributes={"alt": img_match.group(1)}
                )
            
            # Regular paragraph
            return MarkdownElement(
                type=ElementType.PARAGRAPH,
                content=text
            )
            
        elif node.type in ("bullet_list", "ordered_list"):
            list_type = ElementType.LIST_ORDERED if node.type == "ordered_list" else ElementType.LIST_UNORDERED
            element = MarkdownElement(type=list_type, content="")
            
            # Process list items
            for item in node.children:
                if item.type == "list_item":
                    item_text = self._get_text_content(item)
                    element.children.append(
                        MarkdownElement(type=ElementType.PARAGRAPH, content=item_text)
                    )
            
            return element
            
        elif node.type == "code_block":
            return MarkdownElement(
                type=ElementType.CODE_BLOCK,
                content=node.content,
                attributes={"language": node.info if hasattr(node, 'info') else ""}
            )
            
        elif node.type == "table":
            return self._parse_table(node)
            
        return None
        
    def _parse_table(self, node: SyntaxTreeNode) -> MarkdownElement:
        """Parse a table node into a MarkdownElement"""
        table_element = MarkdownElement(type=ElementType.TABLE, content="")
        
        # Extract headers and rows
        headers = []
        rows = []
        
        for child in node.children:
            if child.type == "thead":
                for row in child.children:
                    if row.type == "tr":
                        headers = [self._get_text_content(cell) for cell in row.children]
            elif child.type == "tbody":
                for row in child.children:
                    if row.type == "tr":
                        row_data = [self._get_text_content(cell) for cell in row.children]
                        rows.append(row_data)
        
        table_element.attributes = {
            "headers": headers,
            "rows": rows
        }
        
        return table_element
        
    def _get_text_content(self, node: SyntaxTreeNode) -> str:
        """Extract text content from a node"""
        if hasattr(node, 'content') and node.content:
            return node.content
        
        text_parts = []
        if hasattr(node, 'children'):
            for child in node.children:
                if child.type == "text":
                    text_parts.append(child.content)
                elif child.type == "inline":
                    text_parts.append(self._get_text_content(child))
                else:
                    # Recursively get text from nested elements
                    text_parts.append(self._get_text_content(child))
        
        return " ".join(text_parts).strip()
        
    def _extract_mermaid(self, text: str) -> Optional[str]:
        """Extract Mermaid diagram content from text"""
        match = re.search(r'```mermaid\s*\n(.*?)\n```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
        
    def _get_next_sibling(self, node: SyntaxTreeNode) -> Optional[SyntaxTreeNode]:
        """Get the next sibling of a node"""
        if not node.parent:
            return None
            
        siblings = node.parent.children
        node_index = siblings.index(node)
        
        if node_index + 1 < len(siblings):
            return siblings[node_index + 1]
        
        return None
        
    def _collect_until_heading(self, start_node: SyntaxTreeNode, original_content: str) -> str:
        """Collect content from start node until next heading"""
        # For now, return the heading text
        # In a full implementation, this would extract the actual content
        return self._get_text_content(start_node)
        
    def _collect_section_content(self, heading_node: SyntaxTreeNode, original_content: str) -> str:
        """Collect all content for a section (H2 and its content)"""
        # For now, return the heading text
        # In a full implementation, this would extract the entire section
        return self._get_text_content(heading_node)