import unittest
import os
import shutil
import tempfile
import json
from navigator.core.navigator import FileNavigator

class TestFileNavigator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test directory structure
        self.chapter1_dir = os.path.join(self.test_dir, "chapter_1")
        self.chapter2_dir = os.path.join(self.test_dir, "chapter_2")
        self.season1_dir = os.path.join(self.chapter1_dir, "season_1")
        self.season2_dir = os.path.join(self.chapter1_dir, "season_2")
        self.update1_dir = os.path.join(self.season1_dir, "1.0")
        
        os.makedirs(self.chapter1_dir)
        os.makedirs(self.chapter2_dir)
        os.makedirs(self.season1_dir)
        os.makedirs(self.season2_dir)
        os.makedirs(self.update1_dir)
        
        # Create test JSON files
        self.update1_json = os.path.join(self.update1_dir, "1.0.json")
        with open(self.update1_json, 'w') as f:
            json.dump({"locations": ["Tilted Towers", "Pleasant Park", "Retail Row"]}, f)
            
        self.update2_dir = os.path.join(self.season2_dir, "2.0")
        os.makedirs(self.update2_dir)
        self.update2_json = os.path.join(self.update2_dir, "2.0.json")
        with open(self.update2_json, 'w') as f:
            json.dump({"locations": ["Lazy Links", "Paradise Palms", "Tilted Towers"]}, f)
        
        # Create a navigator instance
        self.navigator = FileNavigator(self.test_dir)
        
    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_init(self):
        """Test initialization of FileNavigator"""
        self.assertEqual(self.navigator.base_dir, os.path.abspath(self.test_dir))
        self.assertEqual(self.navigator.current_path, os.path.abspath(self.test_dir))
        self.assertEqual(self.navigator.entries, [])
        
    def test_update_entries(self):
        """Test updating the list of entries in current directory"""
        self.navigator.update_entries()
        self.assertEqual(set(self.navigator.entries), {"chapter_1", "chapter_2"})
        
    def test_go_up(self):
        """Test navigating up a directory"""
        # First navigate to chapter_1
        self.navigator.update_entries()
        self.navigator.current_path = os.path.join(self.test_dir, "chapter_1")
        self.navigator.update_entries()
        
        # Then go up
        self.navigator.go_up()
        self.assertEqual(self.navigator.current_path, os.path.abspath(self.test_dir))
        
    def test_enter(self):
        """Test entering a directory"""
        self.navigator.update_entries()
        
        # Test entering chapter_1
        result = self.navigator.enter(0)  # assuming chapter_1 is first in entries
        self.assertIsNone(result)
        self.assertEqual(self.navigator.current_path, os.path.abspath(self.chapter1_dir))
        
    def test_read_file(self):
        """Test reading a JSON file"""
        lines = self.navigator.read_file(self.update1_json)
        self.assertTrue(any("Tilted Towers" in line for line in lines))
        
    def test_search_locations(self):
        """Test searching for locations"""
        results = self.navigator.search_locations("Tilted")
        
        # We expect to find matches in both chapter_1/season_1 and chapter_1/season_2
        self.assertEqual(len(results), 2)
        
        # Results should be sorted by chapter/season
        self.assertEqual(results[0][0], "chapter_1/season_1")
        self.assertEqual(results[1][0], "chapter_1/season_2")
        
        # Check that 1.0 update is found in first result
        self.assertIn("1.0", results[0][1])
        
        # Check that 2.0 update is found in second result
        self.assertIn("2.0", results[1][1])
        
        # Test search with no results
        results = self.navigator.search_locations("nonexistent")
        self.assertEqual(len(results), 0)
        
if __name__ == '__main__':
    unittest.main()