import unittest
import os
import shutil
import tempfile
from core.repository import Repository

class TestRepository(unittest.TestCase):
    def setUp(self):
        # Create a temp repo structure
        self.test_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.test_dir, "utils"))
        
        # Create dummy file
        self.file_path = os.path.join(self.test_dir, "utils", "helper.py")
        with open(self.file_path, "w") as f:
            f.write("def help(): pass")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_populates_files(self):
        """Verify repository uses ingestor to load files."""
        repo = Repository(self.test_dir)
        repo.load()
        
        files = repo.list_files()
        self.assertIn("utils/helper.py", files)
        
        # Verify content access
        source = repo.get_file("utils/helper.py")
        self.assertIsNotNone(source)
        self.assertEqual(source.content, "def help(): pass")

    def test_spec_storage(self):
        """Verify we can attach specs to files."""
        repo = Repository(self.test_dir)
        repo.load()
        
        target = "utils/helper.py"
        dummy_spec = "# Spec for Helper"
        
        repo.save_spec(target, dummy_spec)
        self.assertEqual(repo.get_spec(target), dummy_spec)

    def test_save_spec_invalid_file(self):
        """Verify we cannot save a spec for a non-existent file."""
        repo = Repository(self.test_dir)
        repo.load()
        
        with self.assertRaises(ValueError):
            repo.save_spec("ghost.py", "# Ghost Spec")

if __name__ == '__main__':
    unittest.main()