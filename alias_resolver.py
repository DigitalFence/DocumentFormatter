#!/usr/bin/env python3
"""
macOS Alias Resolver
Resolves macOS alias files to their actual file paths.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


def resolve_macos_alias(file_path: str) -> str:
    """
    Resolve a macOS alias to its target file path.
    
    Args:
        file_path: Path that might be an alias
        
    Returns:
        The resolved path if it's an alias, or the original path if not
    """
    file_path = Path(file_path)
    
    # If file doesn't exist, return as-is
    if not file_path.exists():
        return str(file_path)
    
    # Check if it's an alias using the 'file' command
    try:
        result = subprocess.run(
            ['file', str(file_path)],
            capture_output=True,
            text=True
        )
        
        if 'MacOS Alias file' not in result.stdout:
            # Not an alias, return original path
            return str(file_path)
    except:
        # If 'file' command fails, return original path
        return str(file_path)
    
    # It's an alias - try to resolve it using AppleScript
    try:
        # AppleScript to resolve alias - using different approach
        script = f'''
        set aliasPath to POSIX file "{file_path}"
        tell application "Finder"
            set originalItem to original item of alias file aliasPath
            return POSIX path of (originalItem as text)
        end tell
        '''
        
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            resolved_path = result.stdout.strip()
            # Verify the resolved path exists
            if Path(resolved_path).exists():
                return resolved_path
    except Exception as e:
        print(f"Warning: Could not resolve alias {file_path}: {e}")
    
    # If resolution fails, try using 'readlink' as fallback
    try:
        result = subprocess.run(
            ['readlink', str(file_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            resolved = result.stdout.strip()
            if Path(resolved).exists():
                return resolved
    except:
        pass
    
    # If all methods fail, return original path
    return str(file_path)


def resolve_path(file_path: str) -> str:
    """
    Resolve a path, handling both aliases and symbolic links.
    
    Args:
        file_path: Path that might be an alias or symlink
        
    Returns:
        The fully resolved path
    """
    # First resolve any symlinks
    file_path = Path(file_path).resolve()
    
    # Then check if it's a macOS alias
    return resolve_macos_alias(str(file_path))


if __name__ == "__main__":
    # Test the resolver
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        resolved = resolve_path(path)
        print(f"Original: {path}")
        print(f"Resolved: {resolved}")
    else:
        print("Usage: python alias_resolver.py <file_path>")