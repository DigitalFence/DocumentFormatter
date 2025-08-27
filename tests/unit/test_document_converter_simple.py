"""
Unit tests for document_converter_simple.py module.
Tests the simplified document converter functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import after path setup in conftest.py
from document_converter_simple import main


class TestDocumentConverterSimple:
    """Test cases for the simple document converter."""
    
    @pytest.mark.unit
    def test_main_with_reference_argument(self, reference_doc_path, sample_text_file, temp_dir, capsys):
        """Test main function with reference argument provided."""
        # Arrange
        output_path = temp_dir / f"{sample_text_file.stem}_formatted.docx"
        test_args = ['script_name', str(sample_text_file), '--reference', str(reference_doc_path)]
        
        # Act
        with patch('sys.argv', test_args):
            with patch('document_converter_simple.DocumentConverter') as mock_converter_class:
                mock_converter = MagicMock()
                mock_converter_class.return_value = mock_converter
                
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0  # Should exit successfully
                
        # Assert
        mock_converter_class.assert_called_once_with(str(reference_doc_path))
        mock_converter.convert.assert_called_once_with(str(sample_text_file), str(output_path))
        
        captured = capsys.readouterr()
        assert f"Converting: {sample_text_file.name}" in captured.out
        assert f"Using reference: {reference_doc_path}" in captured.out
    
    @pytest.mark.unit
    def test_main_with_default_reference_in_script_dir(self, sample_text_file, temp_dir, capsys):
        """Test main function finding reference in script directory."""
        # Arrange - Create reference file in script directory
        script_dir = Path(__file__).parent.parent.parent  # Go up to project root
        ref_path = script_dir / "referenceformat.docx"
        
        test_args = ['script_name', str(sample_text_file)]
        
        # Act
        with patch('sys.argv', test_args):
            with patch('document_converter_simple.Path.exists') as mock_exists:
                # Mock that reference exists in script directory
                def mock_exists_func(self):
                    return str(self).endswith('referenceformat.docx') and 'scripts/wordformatterbyclaude' in str(self)
                mock_exists.side_effect = mock_exists_func
                
                with patch('document_converter_simple.DocumentConverter') as mock_converter_class:
                    mock_converter = MagicMock()
                    mock_converter_class.return_value = mock_converter
                    
                    try:
                        main()
                    except SystemExit as e:
                        assert e.code == 0
                
        # Assert
        mock_converter_class.assert_called_once()
        # The exact path will vary, but should end with referenceformat.docx
        call_args = mock_converter_class.call_args[0][0]
        assert call_args.endswith('referenceformat.docx')
    
    @pytest.mark.unit
    def test_main_with_reference_in_documents(self, sample_text_file, temp_dir, capsys):
        """Test main function finding reference in Documents folder."""
        # Arrange
        test_args = ['script_name', str(sample_text_file)]
        
        # Act
        with patch('sys.argv', test_args):
            with patch('document_converter_simple.Path.exists') as mock_exists:
                # Mock that reference exists in Documents folder but not script dir
                def mock_exists_func(self):
                    return 'Documents' in str(self) and str(self).endswith('referenceformat.docx')
                mock_exists.side_effect = mock_exists_func
                
                with patch('document_converter_simple.DocumentConverter') as mock_converter_class:
                    mock_converter = MagicMock()
                    mock_converter_class.return_value = mock_converter
                    
                    try:
                        main()
                    except SystemExit as e:
                        assert e.code == 0
                
        # Assert
        mock_converter_class.assert_called_once()
        call_args = mock_converter_class.call_args[0][0]
        assert 'Documents' in call_args and call_args.endswith('referenceformat.docx')
    
    @pytest.mark.unit
    def test_main_with_reference_on_desktop(self, sample_text_file, temp_dir, capsys):
        """Test main function finding reference on Desktop."""
        # Arrange
        test_args = ['script_name', str(sample_text_file)]
        
        # Act
        with patch('sys.argv', test_args):
            with patch('document_converter_simple.Path.exists') as mock_exists:
                # Mock that reference exists on Desktop but not in other locations
                def mock_exists_func(self):
                    return 'Desktop' in str(self) and str(self).endswith('referenceformat.docx')
                mock_exists.side_effect = mock_exists_func
                
                with patch('document_converter_simple.DocumentConverter') as mock_converter_class:
                    mock_converter = MagicMock()
                    mock_converter_class.return_value = mock_converter
                    
                    try:
                        main()
                    except SystemExit as e:
                        assert e.code == 0
                
        # Assert
        mock_converter_class.assert_called_once()
        call_args = mock_converter_class.call_args[0][0]
        assert 'Desktop' in call_args and call_args.endswith('referenceformat.docx')
    
    @pytest.mark.unit
    def test_main_reference_not_found(self, sample_text_file, capsys):
        """Test main function when reference file is not found anywhere."""
        # Arrange
        test_args = ['script_name', str(sample_text_file)]
        
        # Act & Assert
        with patch('sys.argv', test_args):
            with patch('document_converter_simple.Path.exists', return_value=False):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 1  # Should exit with error code
        
        # Check error message
        captured = capsys.readouterr()
        assert "Error: Reference format file not found" in captured.out
        assert "referenceformat.docx" in captured.out
    
    @pytest.mark.unit
    def test_main_custom_reference_not_found(self, sample_text_file, temp_dir, capsys):
        """Test main function when custom reference file doesn't exist."""
        # Arrange
        nonexistent_ref = temp_dir / "nonexistent.docx"
        test_args = ['script_name', str(sample_text_file), '--reference', str(nonexistent_ref)]
        
        # Act & Assert
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
        
        # Check error message
        captured = capsys.readouterr()
        assert f"Error: Reference format file not found: {nonexistent_ref}" in captured.out
    
    @pytest.mark.unit
    def test_main_input_file_not_found(self, reference_doc_path, temp_dir, capsys):
        """Test main function when input file doesn't exist."""
        # Arrange
        nonexistent_input = temp_dir / "nonexistent.txt"
        test_args = ['script_name', str(nonexistent_input), '--reference', str(reference_doc_path)]
        
        # Act & Assert
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
        
        # Check error message
        captured = capsys.readouterr()
        assert f"Error: Input file does not exist: {nonexistent_input}" in captured.out
    
    @pytest.mark.unit
    def test_main_conversion_success(self, reference_doc_path, sample_text_file, capsys):
        """Test successful conversion flow."""
        # Arrange
        test_args = ['script_name', str(sample_text_file), '--reference', str(reference_doc_path)]
        
        # Act
        with patch('sys.argv', test_args):
            with patch('document_converter_simple.DocumentConverter') as mock_converter_class:
                mock_converter = MagicMock()
                mock_converter_class.return_value = mock_converter
                
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0
                
        # Assert
        captured = capsys.readouterr()
        assert f"Converting: {sample_text_file.name}" in captured.out
        assert f"Using reference: {reference_doc_path}" in captured.out
        assert "Success! Output saved to:" in captured.out
    
    @pytest.mark.unit
    def test_main_conversion_error(self, reference_doc_path, sample_text_file, capsys):
        """Test conversion error handling."""
        # Arrange
        test_args = ['script_name', str(sample_text_file), '--reference', str(reference_doc_path)]
        
        # Act & Assert
        with patch('sys.argv', test_args):
            with patch('document_converter_simple.DocumentConverter') as mock_converter_class:
                mock_converter = MagicMock()
                mock_converter.convert.side_effect = Exception("Conversion failed")
                mock_converter_class.return_value = mock_converter
                
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 1
        
        # Check error message
        captured = capsys.readouterr()
        assert "Error during conversion: Conversion failed" in captured.out
    
    @pytest.mark.unit
    def test_main_with_short_arguments(self, reference_doc_path, sample_text_file):
        """Test main function with short argument forms."""
        # Arrange
        test_args = ['script_name', str(sample_text_file), '-r', str(reference_doc_path)]
        
        # Act
        with patch('sys.argv', test_args):
            with patch('document_converter_simple.DocumentConverter') as mock_converter_class:
                mock_converter = MagicMock()
                mock_converter_class.return_value = mock_converter
                
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0
                
        # Assert
        mock_converter_class.assert_called_once_with(str(reference_doc_path))
    
    @pytest.mark.unit
    def test_output_path_generation(self, reference_doc_path, temp_dir):
        """Test that output path is generated correctly."""
        # Arrange
        input_file = temp_dir / "test_document.txt"
        input_file.write_text("Test content")
        expected_output = temp_dir / "test_document_formatted.docx"
        
        test_args = ['script_name', str(input_file), '--reference', str(reference_doc_path)]
        
        # Act
        with patch('sys.argv', test_args):
            with patch('document_converter_simple.DocumentConverter') as mock_converter_class:
                mock_converter = MagicMock()
                mock_converter_class.return_value = mock_converter
                
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0
                
        # Assert
        mock_converter.convert.assert_called_once_with(str(input_file), str(expected_output))
    
    @pytest.mark.unit
    def test_argument_parsing_help(self):
        """Test that help argument works."""
        # Arrange
        test_args = ['script_name', '--help']
        
        # Act & Assert
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Help should exit with code 0
            assert exc_info.value.code == 0
    
    @pytest.mark.unit
    def test_argument_parsing_missing_input(self):
        """Test argument parsing with missing required input file."""
        # Arrange
        test_args = ['script_name']  # Missing input file
        
        # Act & Assert  
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should exit with error code for missing required argument
            assert exc_info.value.code == 2