import os
import sys
import unittest

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.categories import UNSPLASH_CATEGORIES

class TestCategories(unittest.TestCase):
    def test_categories_list_not_empty(self):
        self.assertTrue(len(UNSPLASH_CATEGORIES) > 0)
    
    def test_categories_are_strings(self):
        for category in UNSPLASH_CATEGORIES:
            self.assertIsInstance(category, str)
    
    def test_categories_no_duplicates(self):
        # Check that there are no duplicate categories
        unique_categories = set(UNSPLASH_CATEGORIES)
        self.assertEqual(len(unique_categories), len(UNSPLASH_CATEGORIES))
    
    def test_random_category_exists(self):
        self.assertIn("random", UNSPLASH_CATEGORIES)
    
    def test_common_categories_exist(self):
        # Test that some common categories are included
        common_categories = ["nature", "space", "architecture", "animals", "wallpapers"]
        for category in common_categories:
            self.assertIn(category, UNSPLASH_CATEGORIES)

if __name__ == '__main__':
    unittest.main()
