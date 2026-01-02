import unittest
import os
import shutil
import tempfile
from core.ingestor import Ingestor

class TestIngestor(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure
        self.test_dir = tempfile.mkdtemp()
        
        # 1. Create a valid python file
        os.makedirs(os.path.join(self.test_dir, "src"))
        with open(os.path.join(self.test_dir, "src", "main.py"), "w") as f:
            f.write("print('Hello')")
            
        # 2. Create an ignored file (e.g., .pyc or .txt if not allowed)
        with open(os.path.join(self.test_dir, "ignore_me.log"), "w") as f:
            f.write("log data")

        # 3. Create an ignored directory
        os.makedirs(os.path.join(self.test_dir, "__pycache__"))
        with open(os.path.join(self.test_dir, "__pycache__", "cache.file"), "w") as f:
            f.write("binary data")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_scan_filters_correctly(self):
        """Verify only allowed extensions are read and ignored dirs are skipped."""
        ingestor = Ingestor(self.test_dir, allowed_extensions=['.py'])
        files = ingestor.scan()
        
        # Should only find src/main.py
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "main.py")
        self.assertEqual(files[0].content, "print('Hello')")

    def test_scan_rel_paths(self):
        """Verify paths are relative to the root."""
        ingestor = Ingestor(self.test_dir, allowed_extensions=['.py'])
        files = ingestor.scan()
        
        # Check path format (src/main.py, not /tmp/xyz/src/main.py)
        # Note: os.path.join handles separator differences
        expected = os.path.join("src", "main.py")
        self.assertEqual(files[0].path, expected)

if __name__ == '__main__':
    unittest.main()