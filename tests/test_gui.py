"""
test_gui.py - Basic tests for the fuzzy logic GUI functionality.
"""

import unittest
from fuzzylogic.gui.app import FuzzyLogicGUI


class TestFuzzyLogicGUI(unittest.TestCase):
    """Test cases for the fuzzy logic GUI."""
    
    def setUp(self):
        """Set up test cases."""
        self.gui = FuzzyLogicGUI()
    
    def test_create_domain(self):
        """Test domain creation."""
        domain = self.gui.create_domain('test', 0, 10, 0.5)
        
        self.assertIn('test', self.gui.domains)
        self.assertEqual(domain._low, 0)
        self.assertEqual(domain._high, 10)
        self.assertEqual(domain._res, 0.5)
    
    def test_add_sets(self):
        """Test adding different types of fuzzy sets."""
        # Create domain first
        self.gui.create_domain('test', 0, 10, 0.1)
        
        # Test R function
        self.gui.add_set_to_domain('test', 'high', 'R', {'low': 6, 'high': 10})
        
        # Test S function
        self.gui.add_set_to_domain('test', 'low', 'S', {'low': 0, 'high': 4})
        
        # Test triangular function
        self.gui.add_set_to_domain('test', 'medium', 'triangular', {'low': 3, 'high': 7, 'c': 5})
        
        # Test that sets were added
        domain = self.gui.domains['test']
        self.assertTrue(hasattr(domain, 'high'))
        self.assertTrue(hasattr(domain, 'low'))
        self.assertTrue(hasattr(domain, 'medium'))
    
    def test_test_value(self):
        """Test value testing functionality."""
        # Create domain and sets
        self.gui.create_domain('test', 0, 10, 0.1)
        self.gui.add_set_to_domain('test', 'low', 'S', {'low': 0, 'high': 4})
        self.gui.add_set_to_domain('test', 'high', 'R', {'low': 6, 'high': 10})
        
        # Test value
        result = self.gui.test_value('test', 2)
        
        self.assertIsInstance(result, dict)
        self.assertIn('test.low', result)
        self.assertIn('test.high', result)
        
        # Low value should have high membership in 'low' set
        self.assertGreater(result['test.low'], 0)
        self.assertEqual(result['test.high'], 0)
    
    def test_code_generation(self):
        """Test code generation functionality."""
        # Create domain and sets
        self.gui.create_domain('temp', 0, 40, 0.1)
        self.gui.add_set_to_domain('temp', 'cold', 'S', {'low': 0, 'high': 15})
        self.gui.add_set_to_domain('temp', 'hot', 'R', {'low': 25, 'high': 40})
        
        code = self.gui.generate_code()
        
        # Check that code contains expected elements
        self.assertIn('from fuzzylogic.classes import Domain', code)
        self.assertIn('from fuzzylogic.functions import', code)
        self.assertIn("temp = Domain('temp', 0, 40, res=0.1)", code)
        self.assertIn('temp.cold = S(0, 15)', code)
        self.assertIn('temp.hot = R(25, 40)', code)
    
    def test_plot_domain(self):
        """Test domain plotting functionality."""
        # Create domain and sets
        self.gui.create_domain('test', 0, 10, 0.1)
        self.gui.add_set_to_domain('test', 'low', 'S', {'low': 0, 'high': 4})
        
        # Test plotting
        plot_data = self.gui.plot_domain('test')
        
        # Should return base64 encoded image data
        self.assertIsNotNone(plot_data)
        self.assertIsInstance(plot_data, str)
        self.assertGreater(len(plot_data), 100)  # Should be substantial data
    
    def test_nonexistent_domain(self):
        """Test behavior with nonexistent domain."""
        # Test value on nonexistent domain
        result = self.gui.test_value('nonexistent', 5)
        self.assertIsNone(result)
        
        # Test plot on nonexistent domain
        plot_data = self.gui.plot_domain('nonexistent')
        self.assertIsNone(plot_data)
        
        # Test adding set to nonexistent domain
        with self.assertRaises(ValueError):
            self.gui.add_set_to_domain('nonexistent', 'test', 'R', {'low': 0, 'high': 1})


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)