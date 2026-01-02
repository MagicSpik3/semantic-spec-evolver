from typing import Dict, List, Optional
from core.ingestor import Ingestor, SourceFile

class Repository:
    """
    The Knowledge Base.
    Holds the state of the repository: files, specs, and (eventually) the dependency graph.
    """
    
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.ingestor = Ingestor(root_path)
        self._files: Dict[str, SourceFile] = {} # Key: Relative Path
        self._specs: Dict[str, str] = {}        # Key: Relative Path -> Spec Content

    def load(self):
        """Triggers the Ingestor to scan and load files into memory."""
        scanned_files = self.ingestor.scan()
        for f in scanned_files:
            self._files[f.path] = f

    def get_file(self, relative_path: str) -> Optional[SourceFile]:
        """Retrieves a specific file by its relative path."""
        return self._files.get(relative_path)

    def list_files(self) -> List[str]:
        """Returns a list of all loaded file paths."""
        return sorted(list(self._files.keys()))

    def save_spec(self, relative_path: str, spec_content: str):
        """Stores a generated specification for a file."""
        if relative_path not in self._files:
            raise ValueError(f"File {relative_path} does not exist in repository.")
        self._specs[relative_path] = spec_content

    def get_spec(self, relative_path: str) -> Optional[str]:
        return self._specs.get(relative_path)
