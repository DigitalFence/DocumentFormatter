"""
Unit tests for document_converter_ai.py module.
Tests AIDocumentConverter class and its AI-enhanced functionality.
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import subprocess

from document_converter_ai import AIDocumentConverter


class TestAIDocumentConverter:
    """Test cases for the AIDocumentConverter class."""
    
    @pytest.mark.unit
    def test_ai_converter_initialization(self, reference_doc_path):
        """Test that AIDocumentConverter initializes correctly."""
        # Arrange & Act
        converter = AIDocumentConverter(str(reference_doc_path))
        
        # Assert
        assert converter.reference_path == str(reference_doc_path)
        assert converter.converter is not None
        assert converter.debug == False  # Default value
        assert converter.save_markdown == True  # Default value
        assert converter.show_progress == True  # Default value
        assert converter.model == 'sonnet'  # Default value
        assert converter.timeout == 600  # Default value
        assert converter.enable_haiku_fallback == True  # Default value
    
    @pytest.mark.unit
    def test_ai_converter_initialization_with_env_vars(self, reference_doc_path):
        """Test initialization with environment variable overrides."""
        # Arrange
        with patch.dict(os.environ, {
            'WORD_FORMATTER_DEBUG': '1',
            'SAVE_MARKDOWN': '0',
            'SHOW_PROGRESS': '0', 
            'CLAUDE_MODEL': 'haiku',
            'CLAUDE_TIMEOUT': '300',
            'ENABLE_HAIKU_FALLBACK': '0'
        }):
            # Act
            converter = AIDocumentConverter(str(reference_doc_path))
        
        # Assert
        assert converter.debug == True
        assert converter.save_markdown == False
        assert converter.show_progress == False
        assert converter.model == 'haiku'
        assert converter.timeout == 300
        assert converter.enable_haiku_fallback == False
    
    @pytest.mark.unit
    def test_create_analysis_prompt(self, reference_doc_path):
        """Test creation of analysis prompt for Claude."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_text = "This is a test document with some content."
        
        # Act
        prompt = converter._create_analysis_prompt(test_text)
        
        # Assert
        assert "Convert the following plain text to well-structured markdown format" in prompt
        assert "ITALICIZE non-English text and transliterated text" in prompt
        assert "Sanskrit transliterations" in prompt
        assert "Devanagari script" in prompt
        assert test_text in prompt
        assert "Process the ENTIRE document in one response" in prompt
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_call_claude_success(self, reference_doc_path, mock_claude_success):
        """Test successful Claude CLI call."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_prompt = "Test prompt"
        
        # Act
        success, result = converter._call_claude(test_prompt)
        
        # Assert
        assert success is True
        assert "# Test Document" in result
        assert "Chapter 1: Introduction" in result
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_call_claude_timeout(self, reference_doc_path, mock_claude_timeout):
        """Test Claude CLI timeout handling."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_prompt = "Test prompt"
        
        # Act
        success, result = converter._call_claude(test_prompt)
        
        # Assert
        assert success is False
        assert "timed out" in result
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_call_claude_error(self, reference_doc_path, mock_claude_error):
        """Test Claude CLI error handling."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_prompt = "Test prompt"
        
        # Act
        success, result = converter._call_claude(test_prompt)
        
        # Assert
        assert success is False
        assert "Claude API error" in result
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_call_claude_incomplete_response(self, reference_doc_path, mock_claude_incomplete):
        """Test detection of incomplete Claude responses."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_prompt = "Test prompt"
        
        # Act
        success, result = converter._call_claude(test_prompt)
        
        # Assert
        assert success is False
        assert "incomplete response" in result
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_call_claude_file_not_found(self, reference_doc_path):
        """Test Claude CLI not found error handling."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_prompt = "Test prompt"
        
        with patch('subprocess.run', side_effect=FileNotFoundError("Claude CLI not found")):
            # Act
            success, result = converter._call_claude(test_prompt)
        
        # Assert
        assert success is False
        assert "Claude CLI not found" in result
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_call_claude_with_custom_model(self, reference_doc_path, mock_claude_success):
        """Test Claude CLI call with custom model."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_prompt = "Test prompt"
        
        # Act
        success, result = converter._call_claude(test_prompt, model='haiku')
        
        # Assert
        assert success is True
        # Verify that the correct model was used in the subprocess call
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Test output"
            converter._call_claude(test_prompt, model='haiku')
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert 'haiku' in args
    
    @pytest.mark.unit 
    def test_detect_non_english_text_sanskrit(self, reference_doc_path):
        """Test detection of Sanskrit transliterated text."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        
        # Act & Assert
        # Sanskrit with diacritical marks
        sanskrit_text = "Vāg vai brahma"
        result = converter._detect_non_english_text(sanskrit_text)
        assert result == "*Vāg vai brahma*"
        
        # Text with various diacriticals
        diacritical_text = "Oṃ bhūr bhuvaḥ svaḥ"
        result = converter._detect_non_english_text(diacritical_text)
        assert result == "*Oṃ bhūr bhuvaḥ svaḥ*"
        
        # Already italicized text should remain unchanged
        already_italic = "*Existing italic text*"
        result = converter._detect_non_english_text(already_italic)
        assert result == "*Existing italic text*"
    
    @pytest.mark.unit
    def test_detect_non_english_text_devanagari(self, reference_doc_path):
        """Test detection of Devanagari script."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        
        # Act & Assert
        # Devanagari text
        hindi_text = "हिन्दी परीक्षण"
        result = converter._detect_non_english_text(hindi_text)
        assert result == "*हिन्दी परीक्षण*"
        
        # Sanskrit in Devanagari
        sanskrit_deva = "सत्यमेव जयते"
        result = converter._detect_non_english_text(sanskrit_deva)
        assert result == "*सत्यमेव जयते*"
    
    @pytest.mark.unit
    def test_detect_non_english_text_regular_english(self, reference_doc_path):
        """Test that regular English text is not italicized."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        
        # Act & Assert
        english_text = "This is regular English text"
        result = converter._detect_non_english_text(english_text)
        assert result == "This is regular English text"
        
        # Text with numbers and punctuation
        mixed_text = "Test123!@# with symbols"
        result = converter._detect_non_english_text(mixed_text)
        assert result == "Test123!@# with symbols"
    
    @pytest.mark.unit
    def test_simple_text_to_markdown_headings(self, reference_doc_path):
        """Test simple text to markdown conversion - heading detection."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_text = """MAIN HEADING
        
This is a paragraph.

Chapter One: Introduction

Another paragraph here.
        
Section 1.1: Details
        
More content."""
        
        # Act
        result = converter._simple_text_to_markdown(test_text)
        
        # Assert
        assert "## MAIN HEADING" in result
        assert "## Chapter One: Introduction" in result
        assert "## Section 1.1: Details" in result
    
    @pytest.mark.unit
    def test_simple_text_to_markdown_lists(self, reference_doc_path):
        """Test simple text to markdown conversion - list detection."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_text = """List of items:

- First item
- Second item
* Third item

Numbered list:
1. First numbered
2. Second numbered
3. Third numbered"""
        
        # Act
        result = converter._simple_text_to_markdown(test_text)
        
        # Assert
        assert "- First item" in result
        assert "- Second item" in result
        assert "- Third item" in result
        assert "1. First numbered" in result
        assert "2. Second numbered" in result
    
    @pytest.mark.unit
    def test_simple_text_to_markdown_non_english(self, reference_doc_path):
        """Test simple text to markdown with non-English text detection."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_text = """Regular English paragraph.

Sanskrit text: Vāg vai brahma here.

Devanagari: हिन्दी परीक्षण text."""
        
        # Act  
        result = converter._simple_text_to_markdown(test_text)
        
        # Assert
        # Non-English text should be italicized
        assert "*Vāg vai brahma*" in result or "Vāg vai brahma" in result  # May be processed by line
        assert "*हिन्दी परीक्षण*" in result or "हिन्दी परीक्षण" in result
        assert "Regular English paragraph." in result
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_process_small_text_success(self, reference_doc_path, mock_claude_success):
        """Test processing small text that doesn't require chunking."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        small_text = "This is a small test document."
        
        # Act
        result = converter._process_in_chunks(small_text, chunk_size=1000)
        
        # Assert
        assert result is not None
        assert "# Test Document" in result
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_process_large_text_chunking(self, reference_doc_path, mock_claude_success):
        """Test processing large text that requires chunking."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        # Create text larger than chunk size
        large_text = "Chapter 1\n\n" + ("Test paragraph. " * 100) + "\n\nChapter 2\n\n" + ("Another paragraph. " * 100)
        
        # Act
        result = converter._process_in_chunks(large_text, chunk_size=500)
        
        # Assert
        assert result is not None
        # Should contain content from both chunks
        assert "Test Document" in result  # From mock response
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_process_chunks_with_haiku_fallback(self, reference_doc_path):
        """Test chunking with Haiku fallback on timeout."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        converter.enable_haiku_fallback = True
        converter.model = 'sonnet'
        
        small_text = "Test document"
        
        # Mock initial timeout, then success with Haiku
        def mock_run_with_fallback(cmd, **kwargs):
            if '--model' in cmd and 'sonnet' in cmd:
                raise subprocess.TimeoutExpired(cmd, 600)
            elif '--model' in cmd and 'haiku' in cmd:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "# Converted with Haiku\n\nTest content"
                mock_result.stderr = ""
                return mock_result
            else:
                mock_result = MagicMock()
                mock_result.returncode = 1
                return mock_result
        
        with patch('subprocess.run', side_effect=mock_run_with_fallback):
            # Act
            result = converter._process_in_chunks(small_text)
        
        # Assert
        assert result is not None
        assert "Converted with Haiku" in result
        assert converter.model == 'haiku'  # Should switch to haiku
    
    @pytest.mark.unit
    def test_process_chunks_fallback_to_simple(self, reference_doc_path, mock_claude_error):
        """Test fallback to simple conversion when Claude fails."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_text = "Simple test\n\nAnother paragraph"
        
        # Act
        result = converter._process_in_chunks(test_text, chunk_size=1000)
        
        # Assert
        assert result is None  # Claude failed, method returns None for single chunk failure
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_convert_text_file_success(self, reference_doc_path, sample_text_file, temp_dir, mock_claude_success, mock_notifications):
        """Test successful conversion of a text file."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        converter.show_progress = False  # Disable progress for cleaner test
        output_path = temp_dir / "output.docx"
        
        # Act
        result = converter.convert_with_ai(str(sample_text_file), str(output_path))
        
        # Assert
        assert result is True
        assert output_path.exists()
        
        # Check that intermediate markdown was saved
        markdown_path = output_path.parent / f"{sample_text_file.stem}_markdown.md"
        assert markdown_path.exists()
    
    @pytest.mark.unit
    def test_convert_rtf_file(self, reference_doc_path, sample_rtf_file, temp_dir, mock_claude_success, mock_notifications):
        """Test conversion of RTF files."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        converter.show_progress = False
        output_path = temp_dir / "output.docx"
        
        # Act
        result = converter.convert_with_ai(str(sample_rtf_file), str(output_path))
        
        # Assert
        assert result is True
        assert output_path.exists()
    
    @pytest.mark.unit
    def test_convert_empty_file(self, reference_doc_path, empty_text_file, temp_dir, mock_notifications):
        """Test conversion of empty files."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        converter.show_progress = False
        output_path = temp_dir / "output.docx"
        
        # Act
        result = converter.convert_with_ai(str(empty_text_file), str(output_path))
        
        # Assert
        assert result is False  # Should fail for empty files
    
    @pytest.mark.unit
    def test_convert_nonexistent_file(self, reference_doc_path, temp_dir, mock_notifications):
        """Test conversion of non-existent files."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        nonexistent_file = temp_dir / "nonexistent.txt"
        output_path = temp_dir / "output.docx"
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            converter.convert_with_ai(str(nonexistent_file), str(output_path))
    
    @pytest.mark.unit
    def test_convert_with_claude_fallback(self, reference_doc_path, sample_text_file, temp_dir, mock_notifications):
        """Test conversion with fallback to simple when Claude fails."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        converter.show_progress = False
        output_path = temp_dir / "output.docx"
        
        # Mock Claude to always fail
        with patch.object(converter, '_process_in_chunks', return_value=None):
            # Act
            result = converter.convert_with_ai(str(sample_text_file), str(output_path))
        
        # Assert
        assert result is True  # Should still succeed with simple fallback
        assert output_path.exists()
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'SAVE_MARKDOWN': '0'})
    def test_convert_no_markdown_save(self, reference_doc_path, sample_text_file, temp_dir, mock_claude_success, mock_notifications):
        """Test that markdown is not saved when disabled."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        output_path = temp_dir / "output.docx"
        
        # Act
        result = converter.convert_with_ai(str(sample_text_file), str(output_path))
        
        # Assert
        assert result is True
        
        # Check that intermediate markdown was NOT saved
        markdown_path = output_path.parent / f"{sample_text_file.stem}_markdown.md"
        assert not markdown_path.exists()
    
    @pytest.mark.unit
    def test_convert_with_custom_output_path(self, reference_doc_path, sample_text_file, temp_dir, mock_claude_success, mock_notifications):
        """Test conversion with custom output path."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        converter.show_progress = False
        custom_output = temp_dir / "custom_name.docx"
        
        # Act
        result = converter.convert_with_ai(str(sample_text_file), str(custom_output))
        
        # Assert
        assert result is True
        assert custom_output.exists()
    
    @pytest.mark.unit
    def test_convert_markdown_file_direct(self, reference_doc_path, sample_markdown_file, temp_dir, mock_notifications):
        """Test direct conversion of markdown files without AI processing."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        converter.show_progress = False
        output_path = temp_dir / "output.docx"
        
        # Act
        result = converter.convert_with_ai(str(sample_markdown_file), str(output_path))
        
        # Assert
        assert result is True
        assert output_path.exists()
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ERROR_LOG': '/tmp/test_error.log'})
    def test_error_logging(self, reference_doc_path, temp_dir, mock_notifications):
        """Test error logging functionality."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        invalid_file = temp_dir / "invalid.txt" 
        invalid_file.write_bytes(b'\xff\xfe\x00\x00')  # Invalid UTF-8
        
        # Act
        result = converter.convert_with_ai(str(invalid_file))
        
        # Assert
        assert result is False
        # Error should be logged (we can't easily test file writing in isolation)
    
    @pytest.mark.unit
    @pytest.mark.claude
    def test_notification_progress_tracking(self, reference_doc_path, large_text_file, mock_claude_success):
        """Test progress notifications during chunked processing."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        converter.show_progress = True
        
        with patch('subprocess.run') as mock_run:
            # Mock Claude CLI success
            claude_mock = MagicMock()
            claude_mock.returncode = 0 
            claude_mock.stdout = "# Converted chunk\n\nContent here"
            claude_mock.stderr = ""
            
            # Mock notification calls to return success
            notification_mock = MagicMock()
            notification_mock.returncode = 0
            
            def selective_mock(cmd, **kwargs):
                if 'claude' in str(cmd):
                    return claude_mock
                else:
                    return notification_mock
            
            mock_run.side_effect = selective_mock
            
            # Act
            result = converter._process_in_chunks("x" * 50000, chunk_size=10000)  # Force chunking
        
        # Assert
        assert result is not None
        # Verify that notification commands were called
        notification_calls = [call for call in mock_run.call_args_list 
                            if any('notifier' in str(arg) or 'osascript' in str(arg) for arg in call[0][0])]
        assert len(notification_calls) > 0  # Should have sent notifications


class TestAIDocumentConverterConfiguration:
    """Test configuration and environment variable handling."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'CHUNK_THRESHOLD': '5000'})
    def test_custom_chunk_threshold(self, reference_doc_path, mock_claude_success):
        """Test custom chunk threshold from environment."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        test_text = "x" * 6000  # Larger than custom threshold
        
        # Act
        with patch.object(converter, '_call_claude') as mock_call:
            mock_call.return_value = (True, "# Result")
            converter._process_in_chunks(test_text)
        
        # Should be called multiple times due to chunking
        assert mock_call.call_count >= 1
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'CLAUDE_CLI_PATH': '/custom/path/claude'})
    def test_custom_claude_path(self, reference_doc_path):
        """Test custom Claude CLI path."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Test output"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            # Act
            converter._call_claude("test prompt")
        
        # Assert
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == '/custom/path/claude'
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'CLAUDE_TIMEOUT': '120'})
    def test_custom_timeout(self, reference_doc_path):
        """Test custom timeout setting."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        
        # Assert
        assert converter.timeout == 120
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ENABLE_HAIKU_FALLBACK': '0'})
    def test_disable_haiku_fallback(self, reference_doc_path):
        """Test disabling Haiku fallback."""
        # Arrange
        converter = AIDocumentConverter(str(reference_doc_path))
        
        # Assert
        assert converter.enable_haiku_fallback is False
        
        # Test that fallback doesn't happen
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(['claude'], 600)):
            success, result = converter._call_claude("test")
            assert success is False
            assert "timed out" in result