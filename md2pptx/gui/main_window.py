"""Main GUI window for md2pptx"""

import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
from loguru import logger
import asyncio

from ..parser import MarkdownParser
from ..slides import SlideBuilder
from ..diagrams import MermaidRenderer
from ..parser.models import ElementType


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        """Initialize the main window"""
        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create window
        self.root = ctk.CTk()
        self.root.title("md2pptx - Markdown to PowerPoint Converter")
        self.root.geometry("900x700")
        
        # Variables
        self.template_path = ctk.StringVar()
        self.markdown_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        self.progress_var = ctk.DoubleVar()
        self.log_text = []
        
        # Initialize components
        self.parser = MarkdownParser()
        self.mermaid_renderer = MermaidRenderer()
        
        # Setup UI
        self._setup_ui()
        
        logger.info("GUI initialized")
        
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # File selection section
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        # Template selection
        template_label = ctk.CTkLabel(file_frame, text="PowerPoint Template:")
        template_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        template_entry = ctk.CTkEntry(file_frame, textvariable=self.template_path, width=400)
        template_entry.grid(row=0, column=1, padx=5, pady=5)
        
        template_button = ctk.CTkButton(file_frame, text="Browse", command=self._select_template, width=100)
        template_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Markdown selection
        markdown_label = ctk.CTkLabel(file_frame, text="Markdown File:")
        markdown_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        markdown_entry = ctk.CTkEntry(file_frame, textvariable=self.markdown_path, width=400)
        markdown_entry.grid(row=1, column=1, padx=5, pady=5)
        
        markdown_button = ctk.CTkButton(file_frame, text="Browse", command=self._select_markdown, width=100)
        markdown_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Output selection
        output_label = ctk.CTkLabel(file_frame, text="Output File:")
        output_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        output_entry = ctk.CTkEntry(file_frame, textvariable=self.output_path, width=400)
        output_entry.grid(row=2, column=1, padx=5, pady=5)
        
        output_button = ctk.CTkButton(file_frame, text="Browse", command=self._select_output, width=100)
        output_button.grid(row=2, column=2, padx=5, pady=5)
        
        # Preview section
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        preview_label = ctk.CTkLabel(preview_frame, text="Markdown Structure Preview:")
        preview_label.pack(anchor="w", padx=5, pady=5)
        
        # Tree view for structure
        self.tree = ttk.Treeview(preview_frame, height=10)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Progress section
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready")
        self.progress_label.pack(anchor="w", padx=5, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, variable=self.progress_var)
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        self.progress_bar.set(0)
        
        # Log section
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="x", padx=10, pady=10)
        
        log_label = ctk.CTkLabel(log_frame, text="Log:")
        log_label.pack(anchor="w", padx=5, pady=5)
        
        self.log_textbox = ctk.CTkTextbox(log_frame, height=100)
        self.log_textbox.pack(fill="x", padx=5, pady=5)
        
        # Control buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.convert_button = ctk.CTkButton(
            button_frame, 
            text="Convert", 
            command=self._convert,
            width=200,
            height=40
        )
        self.convert_button.pack(side="left", padx=5)
        
        quit_button = ctk.CTkButton(
            button_frame, 
            text="Quit", 
            command=self.root.quit,
            width=100,
            height=40
        )
        quit_button.pack(side="right", padx=5)
        
    def _select_template(self):
        """Select PowerPoint template file"""
        filename = filedialog.askopenfilename(
            title="Select PowerPoint Template",
            filetypes=[("PowerPoint files", "*.pptx"), ("All files", "*.*")]
        )
        if filename:
            self.template_path.set(filename)
            self._log(f"Selected template: {filename}")
            
    def _select_markdown(self):
        """Select Markdown file"""
        filename = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if filename:
            self.markdown_path.set(filename)
            self._log(f"Selected markdown: {filename}")
            self._preview_markdown(filename)
            
            # Set default output path
            if not self.output_path.get():
                output = Path(filename).with_suffix('.pptx')
                self.output_path.set(str(output))
                
    def _select_output(self):
        """Select output file"""
        filename = filedialog.asksaveasfilename(
            title="Save PowerPoint As",
            defaultextension=".pptx",
            filetypes=[("PowerPoint files", "*.pptx"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            self._log(f"Output will be saved to: {filename}")
            
    def _preview_markdown(self, filename: str):
        """Preview Markdown structure in tree view"""
        try:
            # Clear tree
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Read markdown
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse markdown
            slides = self.parser.parse(content)
            
            # Populate tree
            for i, slide in enumerate(slides):
                slide_text = f"Slide {i+1}: {slide.title}"
                slide_item = self.tree.insert("", "end", text=slide_text)
                
                if slide.lead_text:
                    self.tree.insert(slide_item, "end", text=f"Lead: {slide.lead_text}")
                    
                for element in slide.elements:
                    element_text = f"{element.type.value}: {element.content[:50]}..."
                    self.tree.insert(slide_item, "end", text=element_text)
                    
                self.tree.item(slide_item, open=True)
                
        except Exception as e:
            self._log(f"Error previewing markdown: {e}", "error")
            
    def _log(self, message: str, level: str = "info"):
        """Add message to log"""
        self.log_textbox.insert("end", f"[{level.upper()}] {message}\n")
        self.log_textbox.see("end")
        self.root.update()
        
    def _update_progress(self, value: float, message: str):
        """Update progress bar and label"""
        self.progress_var.set(value)
        self.progress_label.configure(text=message)
        self.root.update()
        
    def _convert(self):
        """Perform the conversion"""
        # Validate inputs
        if not self.markdown_path.get():
            messagebox.showerror("Error", "Please select a Markdown file")
            return
            
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output file")
            return
            
        # Disable button
        self.convert_button.configure(state="disabled")
        
        # Start conversion in thread
        thread = threading.Thread(target=self._convert_thread)
        thread.start()
        
    def _convert_thread(self):
        """Conversion thread"""
        try:
            # Read markdown
            self._update_progress(0.1, "Reading Markdown file...")
            with open(self.markdown_path.get(), 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse markdown
            self._update_progress(0.2, "Parsing Markdown...")
            slides = self.parser.parse(content)
            self._log(f"Parsed {len(slides)} slides")
            
            # Render Mermaid diagrams
            self._update_progress(0.4, "Rendering diagrams...")
            rendered_images = {}
            
            for slide in slides:
                for element in slide.elements:
                    if element.type == ElementType.MERMAID:
                        self._log(f"Rendering Mermaid diagram...")
                        try:
                            # Run async render in sync context
                            image_path = self.mermaid_renderer.render_sync(element.content)
                            rendered_images[element.content] = image_path
                            self._log(f"Rendered diagram to {image_path}")
                        except Exception as e:
                            self._log(f"Failed to render Mermaid: {e}", "error")
                            
            # Build presentation
            self._update_progress(0.7, "Building presentation...")
            builder = SlideBuilder(self.template_path.get() if self.template_path.get() else None)
            
            # Add rendered images
            for mermaid_code, image_path in rendered_images.items():
                builder.add_rendered_image(mermaid_code, image_path)
                
            # Build slides
            builder.build(slides, self.output_path.get())
            
            # Complete
            self._update_progress(1.0, "Conversion complete!")
            self._log(f"Successfully created: {self.output_path.get()}")
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Presentation created successfully!\n{self.output_path.get()}"))
            
        except Exception as e:
            self._log(f"Conversion failed: {e}", "error")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Conversion failed: {e}"))
            
        finally:
            # Re-enable button
            self.root.after(0, lambda: self.convert_button.configure(state="normal"))
            self.root.after(0, lambda: self._update_progress(0, "Ready"))
            
    def run(self):
        """Run the application"""
        self.root.mainloop()