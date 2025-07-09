"""Data models for parsed Markdown content"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class ElementType(Enum):
    """Types of Markdown elements"""
    HEADING1 = "h1"
    HEADING2 = "h2"
    HEADING3 = "h3"
    PARAGRAPH = "paragraph"
    LIST_UNORDERED = "list_unordered"
    LIST_ORDERED = "list_ordered"
    IMAGE = "image"
    CODE_BLOCK = "code_block"
    TABLE = "table"
    MERMAID = "mermaid"


@dataclass
class MarkdownElement:
    """Represents a single Markdown element"""
    type: ElementType
    content: str
    level: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List['MarkdownElement'] = field(default_factory=list)
    

@dataclass
class SlideContent:
    """Represents content for a single slide"""
    title: str
    lead_text: Optional[str] = None
    elements: List[MarkdownElement] = field(default_factory=list)
    notes: str = ""
    slide_index: int = 0
    
    def add_element(self, element: MarkdownElement) -> None:
        """Add an element to the slide"""
        self.elements.append(element)
        
    def set_notes(self, notes: str) -> None:
        """Set speaker notes for the slide"""
        self.notes = notes