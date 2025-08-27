"""
Mock utilities and helpers for testing the Word Formatter system.
Provides reusable mocks for Claude CLI, notifications, and other external dependencies.
"""

import subprocess
from typing import Dict, List, Optional, Callable, Any
from unittest.mock import MagicMock, patch


class ClaudeMockManager:
    """Manages Claude CLI mocking for various test scenarios."""
    
    def __init__(self):
        self.call_count = 0
        self.call_history: List[Dict] = []
        self.response_queue: List[Dict] = []
        self.default_response = {
            'returncode': 0,
            'stdout': self._default_markdown_response(),
            'stderr': ''
        }
    
    def _default_markdown_response(self) -> str:
        """Default Claude response for successful conversion."""
        return """# Converted Document

## Chapter 1: Introduction

This is the converted content with proper markdown formatting.

The AI has structured the text appropriately with headings and paragraphs.

### Section 1.1: Details

More content here with proper formatting applied.

## Chapter 2: Advanced Topics

Additional content showing the AI's text analysis capabilities.

- Bullet points are properly formatted
- Lists are structured correctly
- *Non-English text* is italicized appropriately

## Conclusion

The document has been successfully converted to markdown format."""
    
    def reset(self):
        """Reset the mock state."""
        self.call_count = 0
        self.call_history.clear()
        self.response_queue.clear()
    
    def add_response(self, stdout: str, returncode: int = 0, stderr: str = ''):
        """Add a specific response to the queue."""
        self.response_queue.append({
            'returncode': returncode,
            'stdout': stdout,
            'stderr': stderr
        })
    
    def add_success_response(self, content: str):
        """Add a successful Claude response with custom content."""
        self.add_response(content, returncode=0)
    
    def add_error_response(self, error_msg: str, returncode: int = 1):
        """Add an error response."""
        self.add_response('', returncode=returncode, stderr=error_msg)
    
    def add_timeout_response(self):
        """Add a timeout response (raises TimeoutExpired)."""
        self.response_queue.append('TIMEOUT')
    
    def add_incomplete_response(self):
        """Add an incomplete Claude response that asks for confirmation."""
        incomplete_content = """# Converted Document

## Chapter 1: Introduction

This is the first part of the document.

Would you like me to continue with the rest of the document?"""
        self.add_response(incomplete_content, returncode=0)
    
    def mock_subprocess_run(self, cmd: List[str], **kwargs) -> MagicMock:
        """Mock subprocess.run for Claude CLI calls."""
        self.call_count += 1
        
        # Record the call
        call_record = {
            'call_number': self.call_count,
            'cmd': cmd.copy() if isinstance(cmd, list) else cmd,
            'kwargs': kwargs.copy(),
            'is_claude_call': self._is_claude_call(cmd)
        }
        self.call_history.append(call_record)
        
        # Handle non-Claude calls (like notifications)
        if not self._is_claude_call(cmd):
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ''
            mock_result.stderr = ''
            return mock_result
        
        # Handle timeout scenarios
        if self.response_queue and self.response_queue[0] == 'TIMEOUT':
            self.response_queue.pop(0)
            timeout = kwargs.get('timeout', 600)
            raise subprocess.TimeoutExpired(cmd, timeout)
        
        # Get response (queue or default)
        if self.response_queue:
            response = self.response_queue.pop(0)
        else:
            response = self.default_response
        
        # Create mock result
        mock_result = MagicMock()
        mock_result.returncode = response['returncode']
        mock_result.stdout = response['stdout']
        mock_result.stderr = response['stderr']
        
        return mock_result
    
    def _is_claude_call(self, cmd) -> bool:
        """Check if the command is a Claude CLI call."""
        if isinstance(cmd, list) and len(cmd) > 0:
            cmd_name = cmd[0].lower()
            return 'claude' in cmd_name or cmd_name.endswith('claude')
        return False
    
    def get_claude_calls(self) -> List[Dict]:
        """Get all Claude CLI calls made during testing."""
        return [call for call in self.call_history if call['is_claude_call']]
    
    def get_last_claude_call(self) -> Optional[Dict]:
        """Get the most recent Claude CLI call."""
        claude_calls = self.get_claude_calls()
        return claude_calls[-1] if claude_calls else None


class NotificationMockManager:
    """Manages notification system mocking."""
    
    def __init__(self):
        self.notifications_sent: List[Dict] = []
    
    def reset(self):
        """Reset notification history."""
        self.notifications_sent.clear()
    
    def mock_subprocess_run(self, cmd: List[str], **kwargs) -> MagicMock:
        """Mock subprocess.run for notification calls."""
        
        # Check if this is a notification call
        if self._is_notification_call(cmd):
            # Record the notification
            notification = {
                'cmd': cmd.copy(),
                'kwargs': kwargs.copy(),
                'type': self._get_notification_type(cmd)
            }
            self.notifications_sent.append(notification)
        
        # Always return success for notifications
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ''
        mock_result.stderr = ''
        return mock_result
    
    def _is_notification_call(self, cmd) -> bool:
        """Check if the command is a notification call."""
        if isinstance(cmd, list) and len(cmd) > 0:
            cmd_str = ' '.join(cmd).lower()
            return any(keyword in cmd_str for keyword in [
                'terminal-notifier', 'osascript', 'display notification', 'display alert'
            ])
        return False
    
    def _get_notification_type(self, cmd) -> str:
        """Determine the type of notification."""
        cmd_str = ' '.join(cmd).lower()
        if 'terminal-notifier' in cmd_str:
            return 'terminal-notifier'
        elif 'display alert' in cmd_str:
            return 'alert_dialog'
        elif 'display notification' in cmd_str:
            return 'notification'
        return 'unknown'
    
    def get_notifications_by_type(self, notification_type: str) -> List[Dict]:
        """Get notifications of a specific type."""
        return [n for n in self.notifications_sent if n['type'] == notification_type]


class ComprehensiveMockManager:
    """Comprehensive mock manager that handles all external dependencies."""
    
    def __init__(self):
        self.claude_mock = ClaudeMockManager()
        self.notification_mock = NotificationMockManager()
        self.subprocess_patch = None
    
    def reset_all(self):
        """Reset all mock managers."""
        self.claude_mock.reset()
        self.notification_mock.reset()
    
    def mock_subprocess_run(self, cmd: List[str], **kwargs) -> MagicMock:
        """Comprehensive subprocess.run mock that handles all scenarios."""
        
        # Handle Claude CLI calls
        if self.claude_mock._is_claude_call(cmd):
            return self.claude_mock.mock_subprocess_run(cmd, **kwargs)
        
        # Handle notification calls
        elif self.notification_mock._is_notification_call(cmd):
            return self.notification_mock.mock_subprocess_run(cmd, **kwargs)
        
        # Handle other subprocess calls (like 'which', etc.)
        else:
            mock_result = MagicMock()
            
            # Handle 'which' command for Claude detection
            if isinstance(cmd, list) and len(cmd) >= 2 and cmd[0] == 'which' and 'claude' in cmd[1]:
                # Simulate Claude being found
                mock_result.returncode = 0
                mock_result.stdout = '/usr/local/bin/claude'
            else:
                # Default success for other commands
                mock_result.returncode = 0
                mock_result.stdout = ''
            
            mock_result.stderr = ''
            return mock_result
    
    def start_mocking(self):
        """Start mocking subprocess.run."""
        if self.subprocess_patch is None:
            self.subprocess_patch = patch('subprocess.run', side_effect=self.mock_subprocess_run)
            self.subprocess_patch.start()
    
    def stop_mocking(self):
        """Stop mocking subprocess.run."""
        if self.subprocess_patch is not None:
            self.subprocess_patch.stop()
            self.subprocess_patch = None
    
    def __enter__(self):
        self.start_mocking()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_mocking()


class FileSystemMockManager:
    """Manages file system mocking for testing edge cases."""
    
    def __init__(self):
        self.file_contents: Dict[str, str] = {}
        self.file_permissions: Dict[str, int] = {}
        self.missing_files: List[str] = []
    
    def add_file(self, path: str, content: str, permissions: int = 0o644):
        """Add a mock file with specified content and permissions."""
        self.file_contents[path] = content
        self.file_permissions[path] = permissions
    
    def add_missing_file(self, path: str):
        """Mark a file as missing (will raise FileNotFoundError)."""
        self.missing_files.append(path)
    
    def mock_open(self, path: str, mode: str = 'r', **kwargs):
        """Mock file opening."""
        if path in self.missing_files:
            raise FileNotFoundError(f"No such file or directory: '{path}'")
        
        if path in self.file_contents:
            from io import StringIO
            return StringIO(self.file_contents[path])
        
        # Default behavior for unmocked files
        return open(path, mode, **kwargs)


def create_claude_success_mock(content: Optional[str] = None) -> Callable:
    """Create a simple Claude success mock for testing."""
    if content is None:
        content = """# Test Document

## Chapter 1: Introduction

This is test content that has been processed by Claude AI.

The formatting has been applied correctly with proper structure.

## Conclusion

Document processing completed successfully."""
    
    def mock_run(cmd, **kwargs):
        if isinstance(cmd, list) and any('claude' in str(arg).lower() for arg in cmd):
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = content
            mock_result.stderr = ''
            return mock_result
        else:
            # For non-Claude calls (notifications, etc.)
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ''
            mock_result.stderr = ''
            return mock_result
    
    return mock_run


def create_claude_error_mock(error_msg: str = "Claude API error") -> Callable:
    """Create a Claude error mock for testing error handling."""
    def mock_run(cmd, **kwargs):
        if isinstance(cmd, list) and any('claude' in str(arg).lower() for arg in cmd):
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ''
            mock_result.stderr = error_msg
            return mock_result
        else:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ''
            mock_result.stderr = ''
            return mock_result
    
    return mock_run


def create_claude_timeout_mock(timeout_after: int = 600) -> Callable:
    """Create a Claude timeout mock for testing timeout scenarios."""
    def mock_run(cmd, timeout=None, **kwargs):
        if isinstance(cmd, list) and any('claude' in str(arg).lower() for arg in cmd):
            raise subprocess.TimeoutExpired(cmd, timeout or timeout_after)
        else:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ''
            mock_result.stderr = ''
            return mock_result
    
    return mock_run


def create_notification_mock() -> Callable:
    """Create a mock that only handles notifications."""
    def mock_run(cmd, **kwargs):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ''
        mock_result.stderr = ''
        return mock_result
    
    return mock_run