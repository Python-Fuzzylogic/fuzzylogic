#!/usr/bin/env python3
"""
example_temperature_control.py - Example fuzzy logic system using the GUI.

This example demonstrates how to create a temperature control system
using fuzzy logic with the GUI and then use the generated code.
"""

from fuzzylogic.classes import Domain
from fuzzylogic.functions import R, S, triangular
from fuzzylogic.gui.app import FuzzyLogicGUI


def create_example_system():
    """Create an example temperature control system."""
    
    # Create GUI instance
    gui = FuzzyLogicGUI()
    
    # Create temperature domain (0-40 degrees Celsius)
    gui.create_domain('temperature', 0, 40, 0.1)
    
    # Add fuzzy sets for temperature
    gui.add_set_to_domain('temperature', 'cold', 'S', {'low': 0, 'high': 15})
    gui.add_set_to_domain('temperature', 'warm', 'triangular', {'low': 10, 'high': 30, 'c': 20})
    gui.add_set_to_domain('temperature', 'hot', 'R', {'low': 25, 'high': 40})
    
    # Create fan speed domain (0-100%)
    gui.create_domain('fan_speed', 0, 100, 1)
    
    # Add fuzzy sets for fan speed
    gui.add_set_to_domain('fan_speed', 'slow', 'S', {'low': 0, 'high': 30})
    gui.add_set_to_domain('fan_speed', 'medium', 'triangular', {'low': 20, 'high': 80, 'c': 50})
    gui.add_set_to_domain('fan_speed', 'fast', 'R', {'low': 70, 'high': 100})
    
    return gui


def demonstrate_system():
    """Demonstrate the fuzzy logic system."""
    
    gui = create_example_system()
    
    print("Temperature Control Fuzzy Logic System")
    print("="*50)
    
    # Test various temperature values
    test_temperatures = [5, 12, 18, 22, 28, 35]
    
    for temp in test_temperatures:
        temp_result = gui.test_value('temperature', temp)
        print(f"\nTemperature: {temp}°C")
        for set_name, membership in temp_result.items():
            clean_name = set_name.split('.')[-1]  # Remove domain prefix
            print(f"  {clean_name}: {membership:.3f}")
    
    print("\n" + "="*50)
    print("Generated Python Code:")
    print("="*50)
    print(gui.generate_code())


if __name__ == '__main__':
    demonstrate_system()