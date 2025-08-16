#!/usr/bin/env python3
"""
Setup script for KiCad Hierarchical Parser
Developed for the Master of Muppets project by y3i12
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read version from the parser script
def get_version():
    """Extract version from the main parser file"""
    try:
        parser_file = this_directory / "kicad_hierarchical_parser.py"
        content = parser_file.read_text(encoding='utf-8')
        # Look for version in metadata
        import re
        version_match = re.search(r"'version':\s*'([^']+)'", content)
        if version_match:
            return version_match.group(1)
        return "2.0.0"  # fallback
    except:
        return "2.0.0"

setup(
    name="kicad-hierarchical-parser",
    version=get_version(),
    author="y3i12 and Claude Code (Anthropic)",
    author_email="claude@anthropic.com",
    description="Advanced KiCad schematic parser with full hierarchical sheet support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/y3i12/master_of_muppets",
    project_urls={
        "Bug Reports": "https://github.com/y3i12/master_of_muppets/issues",
        "Source": "https://github.com/y3i12/master_of_muppets/tree/main/claude/tools",
        "Documentation": "https://github.com/y3i12/master_of_muppets/blob/main/claude/tools/README.md",
    },
    py_modules=["kicad_hierarchical_parser"],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ]
    },
    entry_points={
        "console_scripts": [
            "kicad-hierarchical-parser=kicad_hierarchical_parser:main",
            "kicad-parse=kicad_hierarchical_parser:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "kicad", 
        "eda", 
        "schematic", 
        "hierarchical", 
        "parser", 
        "electronics", 
        "pcb", 
        "hardware",
        "design",
        "automation",
        "component",
        "analysis"
    ],
    package_data={
        "": ["LICENSE", "README.md"],
    },
    include_package_data=True,
    zip_safe=False,
)