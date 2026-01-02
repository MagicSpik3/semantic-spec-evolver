import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SourceFile:
    """Represents a single file in the repository."""
    path: str          # Relative path (e.g., 'utils/helper.py')
    name: str          # Filename (e.g., 'helper.py')
    content: str       # Full text content
    extension: str     # e.g., '.py'

class Ingestor:
    """
    The 'Eyes' of the system. 
    Responsibility: Crawl directory, filter junk, load content into memory.
    """
    
    def __init__(self, root_path: str, allowed_extensions: Optional[List[str]] = None):
        self.root_path = os.path.abspath(root_path)
        self.allowed_extensions = allowed_extensions or ['.py', '.md', '.csv']
        self.ignore_dirs = {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode'}

    def scan(self) -> List[SourceFile]:
        """
        Walks the root path and returns a list of SourceFile objects.
        """
        source_files = []

        if not os.path.exists(self.root_path):
            raise FileNotFoundError(f"Repository not found at: {self.root_path}")

        for root, dirs, files in os.walk(self.root_path):
            # 1. Filter directories in-place to prevent recursion into ignored ones
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            for file in files:
                # 2. Filter by extension
                _, ext = os.path.splitext(file)
                if ext.lower() not in self.allowed_extensions:
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.root_path)

                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    source_files.append(SourceFile(
                        path=rel_path,
                        name=file,
                        content=content,
                        extension=ext.lower()
                    ))
                except Exception as e:
                    print(f"⚠️ Warning: Could not read {rel_path}: {e}")

        return sorted(source_files, key=lambda x: x.path)