# KiCad JSON Converter

A comprehensive bidirectional converter between KiCad schematic files (.kicad_sch) and JSON format.

## Features

✅ **Complete Data Preservation**: Captures ALL information from KiCad schematics  
✅ **Bidirectional**: Convert KiCad → JSON and JSON → KiCad (JSON→KiCad coming soon)  
✅ **Hierarchical Support**: Handles complex hierarchical designs  
✅ **Batch Processing**: Convert entire projects at once  
✅ **JSON Compatibility**: All output is valid, queryable JSON  

## Usage

### Single File Conversion

Convert a single schematic to JSON:
```bash
python kicad_json_converter.py to-json input.kicad_sch -o output.json
```

Convert JSON back to schematic:
```bash
python kicad_json_converter.py from-json input.json -o output.kicad_sch
```

### Batch Conversion

Convert entire project hierarchy:
```bash
python kicad_json_converter.py batch root_schematic.kicad_sch -o json_output_dir
```

## What's Included in JSON

The JSON output includes **everything** from the original KiCad file:

### 📋 **Metadata**
- Converter version, source file, KiCad version
- Generator information

### 🔧 **Core Schematic Data**
- `schematicSymbols`: All component instances with positions, values, properties
- `libSymbols`: Library symbol definitions with pins and graphics
- `sheets`: Hierarchical sheet definitions and connections
- `graphicalItems`: Wires, lines, shapes, polylines

### 🏷️ **Labels & Nets**
- `labels`: Local net labels
- `globalLabels`: Global net labels (cross-sheet)
- `hierarchicalLabels`: Sheet interconnection labels
- `junctions`: Wire connection points
- `noConnects`: No-connection markers

### 📐 **Layout & Graphics**
- `paper`: Page size and orientation
- `titleBlock`: Title, revision, company info
- `texts`: Text annotations
- `textBoxes`: Text boxes with borders
- `images`: Embedded images

### 🔌 **Connectivity**
- `busEntries`: Bus connection points
- `busAliases`: Bus naming aliases
- `sheetInstances`: Hierarchical sheet instances
- `symbolInstances`: Component placement instances

## Data Structure

Each object preserves its original KiCad structure with a `_type` field indicating the object class:

```json
{
  "metadata": {
    "converter_version": "1.0.0",
    "source_file": "path/to/schematic.kicad_sch",
    "kicad_version": "7.0",
    "generator": "kicad_sch"
  },
  "schematicSymbols": [
    {
      "_type": "SchematicSymbol",
      "libraryIdentifier": "Device:R",
      "position": {"x": 100.0, "y": 50.0, "angle": 0},
      "properties": [
        {
          "key": "Reference", 
          "value": "R1",
          "position": {"x": 102.0, "y": 45.0}
        }
      ]
    }
  ],
  "sheets": [...],
  "graphicalItems": [...],
  ...
}
```
