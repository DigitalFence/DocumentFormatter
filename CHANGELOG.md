# Changelog

All notable changes to Word Formatter by Claude will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-26

### Added
- **AI-Enhanced Document Conversion**: Intelligent text analysis using Claude AI (Haiku/Sonnet/Opus)
- **Finder Integration**: Right-click Quick Actions for seamless document processing
- **System Notifications**: Real-time feedback with customizable notification types
- **Multi-Model Support**: Choose between Claude Haiku, Sonnet, or Opus models
- **Comprehensive Logging**: Detailed logs to `/tmp/word_formatter.log` for debugging
- **Configuration System**: Environment variables for customization
- **Error Handling**: Graceful fallbacks with clear error messages
- **Progress Feedback**: Emoji-based progress indicators and status updates
- **Intermediate Markdown**: Always save markdown files for transparency
- **Test Suite**: Sample files and comprehensive testing documentation

### Features
- Support for multiple input formats: `.txt`, `.md`, `.markdown`, `.docx`, `.doc`
- Smart style extraction from reference Word documents
- Automatic heading detection and structure enhancement
- List formatting and quote recognition
- PATH resolution for Finder integration compatibility
- Terminal-notifier integration for reliable notifications

### Configuration Options
- `CLAUDE_MODEL`: Choose AI model (haiku/sonnet/opus)
- `SAVE_MARKDOWN`: Control intermediate markdown file saving
- `SHOW_PROGRESS`: Enable/disable progress indicators  
- `CLAUDE_TIMEOUT`: Customize API timeout duration
- `ENABLE_NOTIFICATIONS`: Control system notifications
- `NOTIFICATION_TYPE`: Choose notification style (notification/dialog/none)
- `WORD_FORMATTER_DEBUG`: Enable verbose debug output
- `ERROR_LOG`: Optional error logging to custom files

### Technical Improvements
- Fixed Finder Quick Action PATH restrictions
- Enhanced Claude CLI detection with multiple search locations
- Improved error handling with detailed logging
- Added terminal-notifier for reliable notification delivery
- Comprehensive .gitignore for clean repository management
- MIT License for open source distribution

### Documentation
- Complete README.md with installation and usage instructions
- Technical documentation in CLAUDE.md with test cases
- Finder integration setup guide
- Troubleshooting guides for common issues

### Initial Release Components
- `document_converter_ai.py`: Core AI-enhanced converter
- `document_converter_simple.py`: Fallback simple converter  
- `format_document.sh`: Shell wrapper with logging and notifications
- `install_quick_action.sh`: Finder integration installer
- Sample test files for validation
- Reference document template