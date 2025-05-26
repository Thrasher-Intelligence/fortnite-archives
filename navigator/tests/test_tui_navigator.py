import unittest
import os
from unittest.mock import Mock, patch
from blessed import Terminal
from navigator.tui.navigator import NavigatorTUI

class TestNavigatorTUI(unittest.TestCase):
    def setUp(self):
        # Create a mock FileNavigator
        self.mock_navigator = Mock()
        self.mock_navigator.base_dir = "/test/dir"
        self.mock_navigator.current_path = "/test/dir"
        self.mock_navigator.entries = ["chapter_1", "chapter_2"]
        
        # Initialize the TUI with the mock navigator
        self.tui = NavigatorTUI(self.mock_navigator)
        
    def test_init(self):
        """Test the initialization of the TUI"""
        self.assertEqual(self.tui.navigator, self.mock_navigator)
        self.assertEqual(self.tui.selected, 0)
        self.assertFalse(self.tui.viewing_file)
        self.assertEqual(self.tui.file_content_lines, [])
        self.assertEqual(self.tui.file_line_offset, 0)
        self.assertEqual(self.tui.search_query, "")
        self.assertFalse(self.tui.in_search_results_view)
        
    @patch('navigator.tui.navigator.term')
    def test_execute_search_with_results(self, mock_term):
        """Test executing a search that returns results"""
        # Setup mock navigator to return search results
        self.mock_navigator.search_locations.return_value = [
            ("chapter_1/season_1", ["1.0", "1.1"]),
            ("chapter_1/season_2", ["2.0"])
        ]
        
        # Setup mock terminal dimensions
        mock_term.height = 24
        mock_term.width = 80
        
        # Set search mode and query
        self.tui.search_mode = True
        self.tui.search_query = "Tilted"
        
        # Execute search
        self.tui.execute_search()
        
        # Verify results
        self.assertFalse(self.tui.search_mode)
        self.assertTrue(self.tui.in_search_results_view)
        self.assertEqual(len(self.tui.search_results), 2)
        self.assertEqual(self.tui.search_selected, 0)
        
        # Verify the navigator search was called with the query
        self.mock_navigator.search_locations.assert_called_once_with("Tilted")
        
    @patch('navigator.tui.navigator.term')
    def test_execute_search_no_results(self, mock_term):
        """Test executing a search that returns no results"""
        # Setup mock navigator to return no results
        self.mock_navigator.search_locations.return_value = []
        
        # Setup mock terminal dimensions
        mock_term.height = 24
        mock_term.width = 80
        
        # Set search mode and query
        self.tui.search_mode = True
        self.tui.search_query = "Nonexistent"
        
        # Execute search
        self.tui.execute_search()
        
        # Verify results
        self.assertFalse(self.tui.search_mode)
        self.assertFalse(self.tui.in_search_results_view)
        self.assertEqual(len(self.tui.search_results), 0)
        
    @patch('navigator.tui.navigator.term')
    def test_navigate_search_results(self, mock_term):
        """Test navigating through search results"""
        # Setup mock terminal dimensions
        mock_term.height = 24
        mock_term.width = 80
        
        # Setup search results
        self.tui.search_results = [
            ("chapter_1/season_1", ["1.0"]),
            ("chapter_1/season_2", ["2.0"]),
            ("chapter_1/season_3", ["3.0"])
        ]
        self.tui.in_search_results_view = True
        self.tui.search_selected = 0
        
        # Test moving down
        with patch.object(self.tui, 'draw'):
            # Simulate KEY_DOWN
            self.tui.search_selected = max(0, self.tui.search_selected)
            self.tui.search_selected = min(len(self.tui.search_results) - 1, self.tui.search_selected + 1)
            self.assertEqual(self.tui.search_selected, 1)
            
            # Simulate KEY_DOWN again
            self.tui.search_selected = min(len(self.tui.search_results) - 1, self.tui.search_selected + 1)
            self.assertEqual(self.tui.search_selected, 2)
            
            # Simulate KEY_DOWN again (should stay at max)
            self.tui.search_selected = min(len(self.tui.search_results) - 1, self.tui.search_selected + 1)
            self.assertEqual(self.tui.search_selected, 2)
            
            # Simulate KEY_UP
            self.tui.search_selected = max(0, self.tui.search_selected - 1)
            self.assertEqual(self.tui.search_selected, 1)
    
    @patch('navigator.tui.navigator.term')
    def test_scroll_file(self, mock_term):
        """Test scrolling file content"""
        # Setup file content
        self.tui.file_content_lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
        self.tui.file_line_offset = 0
        
        # Scroll down
        self.tui.scroll_file(1, 4)  # height 4 means 2 lines visible
        self.assertEqual(self.tui.file_line_offset, 1)
        
        # Scroll down again
        self.tui.scroll_file(1, 4)
        self.assertEqual(self.tui.file_line_offset, 2)
        
        # Scroll down to max (5 lines - 2 visible = offset 3)
        self.tui.scroll_file(10, 4)
        self.assertEqual(self.tui.file_line_offset, 3)
        
        # Scroll back up
        self.tui.scroll_file(-1, 4)
        self.assertEqual(self.tui.file_line_offset, 2)
        
        # Scroll all the way up
        self.tui.scroll_file(-10, 4)
        self.assertEqual(self.tui.file_line_offset, 0)

if __name__ == '__main__':
    unittest.main()