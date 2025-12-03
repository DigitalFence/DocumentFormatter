#!/usr/bin/env python3
"""
Configuration loader for Word Formatter
Loads and manages formatting configuration with defaults and overrides.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any


class FormatterConfig:
    """Manages formatter configuration with defaults and overrides."""
    
    DEFAULT_CONFIG = {
        "external_reference_folder": os.path.expanduser("~/WordFormatReference"),
        "reference_template": "ReferenceFormat.dotx",
        "heading_overrides": {},
        "heading_detection": {
            "section_keywords": ["section", "part"],
            "chapter_keywords": ["chapter"],
            "always_use_heading_1_for_chapters": True
        },
        "page_breaks": {
            "before_sections": False,
            "before_chapters": True
        },
        "blockquote_formatting": {
            "remove_em_dashes": True,
            "single_line_spacing": True,
            "center_align": True
        },
        "chapter_separator": {
            "enabled": False,
            "symbol": "❦",
            "symbol_source": None,
            "position": "before",
            "spacing_before": 12,
            "spacing_after": 12,
            "font_size": 14
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration loader.

        Priority order for config files:
        1. Explicit config_path parameter
        2. FORMATTER_CONFIG_PATH environment variable
        3. External reference folder (/Users/KDP/WordFormatReference/formatter_config.json)
        4. If no config found, uses DEFAULT_CONFIG (template styles from .dotx file)

        Args:
            config_path: Path to configuration file. If None, uses search order above.
        """
        self.config = self.DEFAULT_CONFIG.copy()
        config_file = None

        # Priority 1: Explicit path provided
        if config_path:
            config_file = Path(config_path)
            if self.debug:
                print(f"✓ Using explicitly provided config path: {config_file}")

        # Priority 2: Environment variable
        elif os.environ.get('FORMATTER_CONFIG_PATH'):
            env_config = os.environ.get('FORMATTER_CONFIG_PATH')
            if Path(env_config).exists():
                config_file = Path(env_config)
                if self.debug:
                    print(f"✓ Using config from environment variable: {config_file}")

        # Priority 3: External reference folder (from DEFAULT_CONFIG)
        else:
            external_folder = self.DEFAULT_CONFIG.get("external_reference_folder")
            if external_folder:
                external_config_path = Path(external_folder) / "formatter_config.json"
                if external_config_path.exists():
                    config_file = external_config_path
                    if self.debug:
                        print(f"✓ Using config from external reference folder: {config_file}")

        # Load config if found
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
                    self.config_loaded = True
                    self.config_path = str(config_file)
                    if self.debug:
                        print(f"✓ Loaded config from: {config_file}")
            except Exception as e:
                print(f"Warning: Could not load config from {config_file}: {e}")
                self.config_loaded = False
                self.config_path = None
        else:
            # No config file found, use defaults (will use .dotx template styles)
            self.config_loaded = False
            self.config_path = None
            if self.debug:
                print("ℹ No config file found, using defaults + .dotx template styles")

    @property
    def debug(self):
        """Get debug flag from environment."""
        return os.environ.get('WORD_FORMATTER_DEBUG', '0') == '1'
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Merge user configuration with defaults."""
        # Deep merge the configuration
        for key, value in user_config.items():
            if isinstance(value, dict) and key in self.config:
                # Merge dictionaries
                self.config[key].update(value)
            else:
                # Replace value
                self.config[key] = value
    
    def get_heading_override(self, heading_level: int) -> Optional[Dict[str, Any]]:
        """Get heading style override for a specific level.

        Args:
            heading_level: The heading level (1-6)

        Returns:
            Dictionary of style overrides or None if no overrides defined
        """
        heading_key = f"heading_{heading_level}"
        overrides = self.config.get("heading_overrides", {})

        if heading_key in overrides:
            override = overrides[heading_key]
            # Filter out null values
            return {k: v for k, v in override.items() if v is not None and k != "comment"}

        return None

    def get_style_override(self, style_name: str) -> Optional[Dict[str, Any]]:
        """Get style override for a specific style name.

        Args:
            style_name: The style name (e.g., 'Normal', 'Title', 'Subtitle')

        Returns:
            Dictionary of style overrides or None if no overrides defined
        """
        overrides = self.config.get("style_overrides", {})

        if style_name in overrides:
            override = overrides[style_name]
            # Filter out null values
            return {k: v for k, v in override.items() if v is not None and k != "comment"}

        return None
    
    def should_apply_page_break(self, element_type: str) -> bool:
        """Check if page break should be applied before element.
        
        Args:
            element_type: 'section' or 'chapter'
            
        Returns:
            True if page break should be applied
        """
        page_breaks = self.config.get("page_breaks", {})
        if element_type == "section":
            return page_breaks.get("before_sections", False)
        elif element_type == "chapter":
            return page_breaks.get("before_chapters", True)
        return False
    
    def should_preserve_original_page_breaks(self) -> bool:
        """Check if original page breaks should be preserved."""
        return self.config.get("page_breaks", {}).get("preserve_original", True)
    
    def should_add_page_break_after_title(self) -> bool:
        """Check if page break should be added after title."""
        return self.config.get("page_breaks", {}).get("after_title", True)
    
    def should_add_page_break_after_dedication(self) -> bool:
        """Check if page break should be added after dedication."""
        return self.config.get("page_breaks", {}).get("after_dedication", True)
    
    def should_add_page_break_after_contents(self) -> bool:
        """Check if page break should be added after contents."""
        return self.config.get("page_breaks", {}).get("after_contents", True)
    
    def is_section_keyword(self, text: str) -> bool:
        """Check if text contains section keywords."""
        keywords = self.config.get("heading_detection", {}).get("section_keywords", ["section", "part"])
        return any(keyword in text.lower() for keyword in keywords)
    
    def is_chapter_keyword(self, text: str) -> bool:
        """Check if text contains chapter keywords."""
        keywords = self.config.get("heading_detection", {}).get("chapter_keywords", ["chapter"])
        return any(keyword in text.lower() for keyword in keywords)
    
    def is_title_keyword(self, text: str) -> bool:
        """Check if text contains title keywords."""
        keywords = self.config.get("heading_detection", {}).get("title_keywords", ["title"])
        return any(keyword in text.lower() for keyword in keywords)
    
    def is_dedication_keyword(self, text: str) -> bool:
        """Check if text contains dedication keywords."""
        keywords = self.config.get("heading_detection", {}).get("dedication_keywords", ["dedicated to", "dedication"])
        return any(keyword in text.lower() for keyword in keywords)
    
    def is_contents_keyword(self, text: str) -> bool:
        """Check if text contains contents/table of contents keywords."""
        keywords = self.config.get("heading_detection", {}).get("contents_keywords", ["contents", "table of contents"])
        return any(keyword in text.lower() for keyword in keywords)
    
    def get_chapter_opening_settings(self) -> Dict[str, Any]:
        """Get settings for chapter opening quotes/verses."""
        return self.config.get("chapter_opening_quote", {})
    
    def get_chapter_closing_settings(self) -> Dict[str, Any]:
        """Get settings for chapter closing content."""
        return self.config.get("chapter_closing_content", {})
    
    def get_hierarchical_list_settings(self) -> Dict[str, Any]:
        """Get settings for hierarchical list formatting."""
        return self.config.get("special_content_formatting", {}).get("hierarchical_lists", {})
    
    def get_blockquote_settings(self) -> Dict[str, Any]:
        """Get blockquote formatting settings."""
        return self.config.get("blockquote_formatting", {})
    
    def resolve_reference_file(self, filename: str) -> Optional[Path]:
        """Resolve path to a reference file (template or symbols).

        Looks in the following order:
        1. External reference folder (if configured)
        2. Local References/ folder
        3. Script directory

        Args:
            filename: Name of the reference file (e.g., "referenceformat.docx", "Symbols.docx")

        Returns:
            Path to the file if found, None otherwise
        """
        script_dir = Path(__file__).parent

        # Check external reference folder first
        external_folder = self.config.get("external_reference_folder")
        if external_folder:
            external_path = Path(external_folder) / filename
            if external_path.exists():
                return external_path

        # Check local References folder
        local_ref_path = script_dir / "References" / filename
        if local_ref_path.exists():
            return local_ref_path

        # Check script directory
        script_path = script_dir / filename
        if script_path.exists():
            return script_path

        return None

    def get_reference_template_path(self) -> Optional[Path]:
        """Get path to the reference template document.

        Returns:
            Path to referenceformat.docx if found, None otherwise
        """
        template_name = self.config.get("reference_template", "referenceformat.docx")
        return self.resolve_reference_file(template_name)

    def get_symbols_file_path(self) -> Optional[Path]:
        """Get path to the symbols document.

        Returns:
            Path to Symbols.docx if found, None otherwise
        """
        separator_config = self.config.get("chapter_separator", {})
        symbol_source = separator_config.get("symbol_source")

        if not symbol_source:
            return None

        # If symbol_source is an absolute path, use it directly
        symbol_path = Path(symbol_source)
        if symbol_path.is_absolute() and symbol_path.exists():
            return symbol_path

        # Otherwise, resolve it using the folder hierarchy
        return self.resolve_reference_file(symbol_source)

    def get_chapter_separator(self) -> Dict[str, Any]:
        """Get chapter separator settings with resolved symbol or image."""
        settings = self.config.get("chapter_separator", {}).copy()

        # If a symbol source is specified, try to extract image from it
        if settings.get("symbol_source") and settings.get("enabled"):
            try:
                # Use the new path resolution method
                symbol_path = self.get_symbols_file_path()
                if not symbol_path:
                    return settings

                from image_extractor import extract_first_image

                # Additional check if file exists and is readable
                if symbol_path.exists():
                    result = extract_first_image(str(symbol_path))
                    if result:
                        image_data, width, height = result
                        settings["image_data"] = image_data
                        settings["image_width"] = width or 0.5  # Default width if not found
                        settings["image_height"] = height or 0.5  # Default height
                        settings["use_image"] = True
                    else:
                        # No image found, try text symbols as fallback
                        try:
                            from symbol_extractor import get_first_symbol
                            symbol = get_first_symbol(symbol_path)
                            settings["symbol"] = symbol
                            settings["use_image"] = False
                        except:
                            settings["use_image"] = False
                else:
                    print(f"Warning: Symbol source file not found: {symbol_path}")
                    settings["use_image"] = False
            except Exception as e:
                import os
                print(f"Warning: Could not extract image/symbol from {settings['symbol_source']}: {e}")
                print(f"  Current working directory: {os.getcwd()}")
                print(f"  Resolved path: {symbol_path}")
                settings["use_image"] = False
        else:
            settings["use_image"] = False
        
        return settings
    
    def save_config(self, path: Optional[str] = None):
        """Save current configuration to file.
        
        Args:
            path: Path to save config to. If None, saves to original path or default.
        """
        if not path:
            path = self.config_path or "formatter_config.json"
        
        with open(path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"Configuration saved to: {path}")


if __name__ == "__main__":
    # Test configuration loading
    config = FormatterConfig()
    
    print("Configuration loaded:", config.config_loaded)
    if config.config_loaded:
        print(f"Config path: {config.config_path}")
    
    print("\nHeading 3 overrides:", config.get_heading_override(3))
    print("Heading 4 overrides:", config.get_heading_override(4))
    print("\nShould apply page break before section:", config.should_apply_page_break("section"))
    print("Should apply page break before chapter:", config.should_apply_page_break("chapter"))