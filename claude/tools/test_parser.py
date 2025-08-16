#!/usr/bin/env python3
"""
Test suite for KiCad Hierarchical Parser
Basic validation and regression tests
"""

import unittest
import tempfile
import json
from pathlib import Path
from kicad_hierarchical_parser import KiCadHierarchicalParser, Component, SheetInstance

class TestKiCadParser(unittest.TestCase):
    """Test cases for the hierarchical parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = KiCadHierarchicalParser()
        
    def test_component_creation(self):
        """Test Component dataclass creation"""
        comp = Component(
            reference="U1",
            value="TL074",
            footprint="SOIC-14",
            lib_id="Amplifier_Operational:TL074",
            sheet_path="/test/path",
            instance_path="/main/"
        )
        
        self.assertEqual(comp.reference, "U1")
        self.assertEqual(comp.value, "TL074")
        self.assertEqual(comp.lib_id, "Amplifier_Operational:TL074")
        self.assertIsInstance(comp.properties, dict)
        
    def test_sheet_instance_creation(self):
        """Test SheetInstance dataclass creation"""
        sheet = SheetInstance(
            name="AMP_Sheet",
            file_path="amp.kicad_sch",
            uuid="test-uuid-123",
            instance_path="/dac/amp/",
            parent_path="/dac/"
        )
        
        self.assertEqual(sheet.name, "AMP_Sheet")
        self.assertEqual(sheet.file_path, "amp.kicad_sch")
        self.assertEqual(sheet.multiplicity, 1)  # default value
        
    def test_component_regex_extraction(self):
        """Test component extraction from sample KiCad content"""
        # Sample KiCad S-expression content
        sample_content = '''
        (symbol
          (lib_id "Amplifier_Operational:TL074")
          (at 100 50 0)
          (property "Reference" "U1" (id 0))
          (property "Value" "TL074" (id 1))
          (property "Footprint" "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm" (id 2))
        )
        (symbol
          (lib_id "power:GND")
          (at 200 100 0)
          (property "Reference" "#PWR01" (id 0))
        )
        (symbol
          (lib_id "Device:C")
          (at 150 75 0)
          (property "Reference" "C1" (id 0))
          (property "Value" "100nF" (id 1))
          (property "Footprint" "Capacitor_SMD:C_0805_2012Metric" (id 2))
        )
        '''
        
        components = self.parser._extract_components_regex(sample_content, "test.kicad_sch")
        
        # Should find 2 components (not the power symbol)
        self.assertEqual(len(components), 2)
        
        # Check first component (TL074)
        u1 = next((c for c in components if c.reference == "U1"), None)
        self.assertIsNotNone(u1)
        self.assertEqual(u1.value, "TL074")
        self.assertEqual(u1.lib_id, "Amplifier_Operational:TL074")
        
        # Check second component (capacitor)
        c1 = next((c for c in components if c.reference == "C1"), None)
        self.assertIsNotNone(c1)
        self.assertEqual(c1.value, "100nF")
        self.assertEqual(c1.lib_id, "Device:C")
        
    def test_sheet_regex_extraction(self):
        """Test sheet extraction from sample KiCad content"""
        sample_content = '''
        (sheet
          (at 100 100)
          (size 50 25)
          (stroke (width 0.1524) (type solid) (color 0 0 0 0))
          (fill (color 0 0 0 0.0000))
          (uuid "12345678-1234-1234-1234-123456789abc")
          (property "Sheetname" "AMP_Module" (id 0) (at 100 120 0))
          (property "Sheetfile" "amp.kicad_sch" (id 1) (at 100 115 0))
        )
        (sheet
          (at 200 100)
          (size 50 25)
          (stroke (width 0.1524) (type solid) (color 0 0 0 0))
          (fill (color 0 0 0 0.0000))
          (uuid "87654321-4321-4321-4321-cba987654321")
          (property "Sheetname" "DAC_Module" (id 0) (at 200 120 0))
          (property "Sheetfile" "dac.kicad_sch" (id 1) (at 200 115 0))
        )
        '''
        
        sheets = self.parser._extract_sheets_regex(sample_content)
        
        # Should find 2 sheets
        self.assertEqual(len(sheets), 2)
        
        # Check first sheet
        amp_sheet = next((s for s in sheets if s.name == "AMP_Module"), None)
        self.assertIsNotNone(amp_sheet)
        self.assertEqual(amp_sheet.file_path, "amp.kicad_sch")
        
        # Check second sheet  
        dac_sheet = next((s for s in sheets if s.name == "DAC_Module"), None)
        self.assertIsNotNone(dac_sheet)
        self.assertEqual(dac_sheet.file_path, "dac.kicad_sch")
        
    def test_main_schematic_detection(self):
        """Test detection of main schematic file"""
        # Mock some sheet templates
        self.parser.sheet_templates = {
            "main.kicad_sch": {
                "sheets": [
                    {"file_path": "dac.kicad_sch", "name": "DAC1"},
                    {"file_path": "dac.kicad_sch", "name": "DAC2"}
                ]
            },
            "dac.kicad_sch": {
                "sheets": [
                    {"file_path": "amp.kicad_sch", "name": "AMP1"}
                ]
            },
            "amp.kicad_sch": {
                "sheets": []
            }
        }
        
        main_schematic = self.parser._find_main_schematic()
        self.assertEqual(main_schematic, "main.kicad_sch")
        
    def test_property_extraction(self):
        """Test property value extraction"""
        test_text = '''
        (property "Reference" "U1" (id 0) (at 100 50 0))
        (property "Value" "TL074" (id 1) (at 100 45 0))
        (property "Footprint" "Package_SO:SOIC-14" (id 2) (at 100 40 0))
        '''
        
        ref = self.parser._extract_property_value(test_text, "Reference")
        value = self.parser._extract_property_value(test_text, "Value")
        footprint = self.parser._extract_property_value(test_text, "Footprint")
        
        self.assertEqual(ref, "U1")
        self.assertEqual(value, "TL074") 
        self.assertEqual(footprint, "Package_SO:SOIC-14")
        
    def test_all_properties_extraction(self):
        """Test extraction of all properties"""
        test_text = '''
        (property "Reference" "U1" (id 0))
        (property "Value" "TL074" (id 1))
        (property "Datasheet" "http://example.com/tl074.pdf" (id 3))
        '''
        
        props = self.parser._extract_all_properties(test_text)
        
        self.assertEqual(len(props), 3)
        self.assertEqual(props["Reference"], "U1")
        self.assertEqual(props["Value"], "TL074")
        self.assertEqual(props["Datasheet"], "http://example.com/tl074.pdf")

class TestMasterOfMuppetsValidation(unittest.TestCase):
    """Validation tests specific to Master of Muppets project"""
    
    def setUp(self):
        """Set up for Master of Muppets testing"""
        self.parser = KiCadHierarchicalParser()
        self.project_dir = Path("../CADfiles/MasterOfMuppets")
        
    def test_master_of_muppets_component_count(self):
        """Test that Master of Muppets project has expected component count"""
        if not self.project_dir.exists():
            self.skipTest(f"Master of Muppets project not found at {self.project_dir}")
            
        result = self.parser.parse_project(self.project_dir)
        
        # Expected values from our analysis
        expected_total = 163
        expected_depth = 4
        
        actual_total = result['summary']['total_components']
        actual_depth = result['summary']['hierarchy_depth']
        
        self.assertEqual(actual_total, expected_total, 
                        f"Expected {expected_total} components, got {actual_total}")
        self.assertEqual(actual_depth, expected_depth,
                        f"Expected hierarchy depth {expected_depth}, got {actual_depth}")
        
    def test_component_type_distribution(self):
        """Test expected component type distribution"""
        if not self.project_dir.exists():
            self.skipTest(f"Master of Muppets project not found at {self.project_dir}")
            
        result = self.parser.parse_project(self.project_dir)
        component_types = result['summary']['component_types']
        
        # Check for expected component types
        self.assertIn('Device', component_types)
        self.assertIn('Amplifier_Operational', component_types)
        
        # Device components should be the most numerous (resistors, capacitors, etc.)
        self.assertGreater(component_types.get('Device', 0), 50)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        self.parser = KiCadHierarchicalParser()
        
    def test_invalid_project_directory(self):
        """Test handling of invalid project directory"""
        invalid_dir = Path("/nonexistent/directory")
        
        # Should not crash, should return empty/default results
        result = self.parser.parse_project(invalid_dir)
        self.assertIsInstance(result, dict)
        self.assertIn('summary', result)
        
    def test_empty_schematic_content(self):
        """Test parsing empty or minimal schematic content"""
        empty_content = "(kicad_sch (version 20211123) (generator eeschema))"
        
        components = self.parser._extract_components_regex(empty_content, "empty.kicad_sch")
        sheets = self.parser._extract_sheets_regex(empty_content)
        
        self.assertEqual(len(components), 0)
        self.assertEqual(len(sheets), 0)
        
    def test_malformed_property(self):
        """Test handling of malformed property syntax"""
        malformed_text = '''
        (property "Reference" "U1"  # Missing closing parenthesis
        (property "BadProperty" incomplete
        (property "GoodProperty" "GoodValue" (id 0))
        '''
        
        # Should extract the well-formed properties (Reference and GoodProperty)
        # BadProperty is malformed and should be skipped
        props = self.parser._extract_all_properties(malformed_text)
        self.assertEqual(len(props), 2)
        self.assertEqual(props.get("Reference"), "U1")
        self.assertEqual(props.get("GoodProperty"), "GoodValue")
        self.assertNotIn("BadProperty", props)

def run_tests():
    """Run all test suites"""
    print("KiCad Hierarchical Parser - Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestKiCadParser))
    suite.addTests(loader.loadTestsFromTestCase(TestMasterOfMuppetsValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("ALL TESTS PASSED!")
    else:
        print(f"TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()