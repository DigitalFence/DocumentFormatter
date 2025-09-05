# Template-Based Document Conversion Implementation Plan

## Problem Statement
The current document converter creates a new blank Word document with default styles (Calibri font, default colors) instead of using the reference document's styles (Aptos Light font, custom colors). This causes output documents to not match the reference document formatting.

## Solution: Template Approach with Optional Config Override

### Core Concept
Use the reference document as a template when creating output documents, preserving all style definitions, fonts, and formatting. The formatter config becomes an optional override mechanism.

## Implementation Steps

### 1. Modify DocumentConverter Class

#### Current Approach (PROBLEMATIC):
```python
self.output_doc = Document()  # Creates blank document with default styles
```

#### New Template Approach:
```python
self.output_doc = Document(self.reference_doc_path)  # Use reference as template
# Clear all content while preserving styles
for element in self.output_doc.element.body:
    self.output_doc.element.body.remove(element)
```

### 2. Add Config Enable/Disable Flag

#### Environment Variable Control:
- `USE_FORMATTER_CONFIG=0` (default - config disabled, pure template)
- `USE_FORMATTER_CONFIG=1` (config enabled for overrides)

#### Implementation in document_converter.py:
```python
def __init__(self, reference_doc_path: str):
    self.use_config = os.environ.get('USE_FORMATTER_CONFIG', '0') == '1'
    
    if self.use_config:
        # Load formatter config for behavioral rules and overrides
        self.config = FormatterConfig.load_config()
    else:
        # Use minimal detection rules only
        self.config = self._get_default_detection_rules()
```

### 3. Page Break Rules for Special Sections

Each of these sections must be on its own page:
- **Title** - First major heading, own page
- **Dedication** - Detection keywords: "dedicated to", "dedication", "in memory of"
- **Contents** - Detection keywords: "contents", "table of contents", "toc"
- **Preface** - Detection keyword: "preface"
- **Foreword** - Detection keyword: "foreword" (note: not "forward")

Implementation approach:
1. Detect section type based on content/keywords
2. Add content with appropriate style
3. Insert page break after section
4. Continue with next content

### 4. Style Application Hierarchy

#### When USE_FORMATTER_CONFIG=0 (Default):
1. Use template document styles directly
2. Apply style by name (Title, Heading 1, etc.)
3. No manual style property application

#### When USE_FORMATTER_CONFIG=1:
1. Use template document styles as base
2. Apply behavioral rules from config (detection, page breaks)
3. Apply style overrides from config if specified

### 5. Config Structure (When Enabled)

```json
{
  "enabled": false,  // Master switch within config
  
  "behavioral_rules": {
    "heading_detection": {
      "title_keywords": ["title"],
      "dedication_keywords": ["dedicated to", "dedication", "in memory of"],
      "contents_keywords": ["contents", "table of contents", "toc"],
      "preface_keywords": ["preface"],
      "foreword_keywords": ["foreword"]
    },
    "page_breaks": {
      "after_title": true,
      "after_dedication": true,
      "after_contents": true,
      "after_preface": true,
      "after_foreword": true,
      "preserve_original": true
    },
    "chapter_separator": {
      "enabled": true,
      "position": "after",
      "symbol_source": "References/Symbols.docx"
    }
  },
  
  "style_overrides": {
    "apply_overrides": false,
    "heading_1": {
      // Optional overrides
    }
  }
}
```

### 6. Testing Plan

#### Test Documents to Create:
1. `test_template_basic.txt` - Simple document with title and headings
2. `test_template_special_sections.txt` - Document with Title, Dedication, Contents, Preface, Foreword
3. `test_template_fonts.txt` - Document to verify Aptos Light font application

#### Test Scenarios:

##### A. Default Template Mode (USE_FORMATTER_CONFIG=0):
```bash
./format_document.sh test_template_basic.txt
```
Expected results:
- ✅ Aptos Light font throughout (not Calibri)
- ✅ Heading colors match reference (#156082)
- ✅ All styles from reference preserved
- ✅ No config file loaded

##### B. Config Enabled Mode (USE_FORMATTER_CONFIG=1):
```bash
USE_FORMATTER_CONFIG=1 ./format_document.sh test_template_basic.txt
```
Expected results:
- ✅ Template styles as base
- ✅ Config behavioral rules applied
- ✅ Any style overrides applied

##### C. Special Sections Test:
```bash
./format_document.sh test_template_special_sections.txt
```
Expected results:
- ✅ Title on its own page
- ✅ Dedication on its own page
- ✅ Contents on its own page
- ✅ Preface on its own page
- ✅ Foreword on its own page

### 7. Files to Modify

1. **document_converter.py**
   - Change Document() to Document(reference_path)
   - Add content clearing logic
   - Add USE_FORMATTER_CONFIG environment check
   - Implement special section detection and page breaks

2. **document_converter_ai.py**
   - Pass USE_FORMATTER_CONFIG to DocumentConverter if needed
   - Ensure AI prompts detect special sections

3. **format_document.sh**
   - Document USE_FORMATTER_CONFIG variable
   - Keep existing functionality

4. **formatter_config.json** (in References/)
   - Update structure for behavioral rules
   - Add special section keywords
   - Set enabled: false by default

### 8. Rollback Plan

If issues arise:
1. Keep old Document() approach in a legacy method
2. Add environment variable to force old behavior: USE_LEGACY_CONVERTER=1
3. Document known issues with template approach

### 9. Success Criteria

- [ ] Fonts match reference document (Aptos Light, not Calibri)
- [ ] Colors match reference (#156082 for headings)
- [ ] Special sections on individual pages
- [ ] Config disabled by default
- [ ] Config overrides work when enabled
- [ ] All existing functionality preserved
- [ ] Tests pass consistently

### 10. Implementation Order

1. First: Implement basic template approach (fixes font issue)
2. Second: Add special section detection and page breaks
3. Third: Add config enable/disable logic
4. Fourth: Test thoroughly with various documents
5. Fifth: Document changes in CLAUDE.md

## Benefits of This Approach

1. **Simplicity**: Template approach is how Word intended style inheritance to work
2. **Reliability**: No manual style extraction and reapplication
3. **Flexibility**: Config remains available for special cases
4. **Performance**: Faster without config parsing by default
5. **Maintainability**: Less code, fewer edge cases

## Potential Challenges and Solutions

### Challenge 1: Clearing template content
**Solution**: Use element-level removal to clear body while preserving style definitions

### Challenge 2: Maintaining section breaks/headers from template
**Solution**: Clear only body paragraphs, not document-level settings

### Challenge 3: Backward compatibility
**Solution**: Environment variable control allows easy switching

## Timeline

- Phase 1 (Immediate): Implement template approach - fixes font issue
- Phase 2 (Next): Add special section handling
- Phase 3 (Optional): Refine config override mechanism

This plan prioritizes fixing the immediate font/style issue while setting up a more robust long-term solution.