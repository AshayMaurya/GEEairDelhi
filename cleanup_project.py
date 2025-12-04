"""
Project Cleanup and Organization Script
Removes unnecessary files and organizes the project structure
"""

import os
import shutil
from pathlib import Path

# Files to remove (not needed for the project)
FILES_TO_REMOVE = [
    'fix_notebook.py',  # Old notebook fix script
    'test_gee.py',  # Test file
    'spatial_mapping_demo.py',  # Demo replaced by notebook integration
    'code.js',  # JavaScript code not needed
    'setup.py',  # Not needed
    'ARCHITECTURE.md',  # Redundant documentation
    'CONFIG_GUIDE.md',  # Redundant documentation
    'EXECUTION_GUIDE.md',  # Redundant documentation
    'FIXES_APPLIED.md',  # Redundant documentation
    'OPTIMIZATIONS.md',  # Redundant documentation
    'PROJECT_SUMMARY.md',  # Redundant documentation
    'QUICKSTART.md',  # Redundant documentation
]

# Directories to clean
DIRS_TO_CLEAN = {
    '__pycache__': True,  # Remove completely
}

def cleanup_project():
    """Clean up unnecessary files"""
    print("=" * 70)
    print("PROJECT CLEANUP")
    print("=" * 70)
    
    removed_count = 0
    
    # Remove files
    print("\nRemoving unnecessary files...")
    for filename in FILES_TO_REMOVE:
        filepath = Path(filename)
        if filepath.exists():
            try:
                filepath.unlink()
                print(f"  ✓ Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Could not remove {filename}: {e}")
        else:
            print(f"  - Not found: {filename}")
    
    # Clean directories
    print("\nCleaning directories...")
    for dirname, remove_completely in DIRS_TO_CLEAN.items():
        dirpath = Path(dirname)
        if dirpath.exists():
            try:
                if remove_completely:
                    shutil.rmtree(dirpath)
                    print(f"  ✓ Removed directory: {dirname}")
                    removed_count += 1
            except Exception as e:
                print(f"  ✗ Could not remove {dirname}: {e}")
    
    print(f"\n✅ Cleanup complete! Removed {removed_count} items")
    
    # Show final structure
    print("\n" + "=" * 70)
    print("FINAL PROJECT STRUCTURE")
    print("=" * 70)
    print("""
GEE/
├── Core Modules
│   ├── config.py                 # Configuration settings
│   ├── data_fetcher.py          # GEE data fetching
│   ├── preprocessing.py         # Data preprocessing
│   ├── models.py                # ML models
│   ├── visualization.py         # Plotting functions
│   ├── spatial_mapper.py        # Geographical mapping
│   └── complete_analysis.py     # Complete pipeline
│
├── Analysis
│   ├── analysis.ipynb           # Main Jupyter notebook
│   └── update_notebook.py       # Notebook updater
│
├── Data & Outputs
│   ├── data/                    # Raw and processed data
│   └── outputs/
│       ├── maps/                # Geographical maps
│       ├── plots/               # Visualizations
│       ├── predictions/         # Model predictions
│       ├── models/              # Saved models
│       └── reports/             # Analysis reports
│
└── Documentation
    ├── README.md                # Main documentation
    ├── STATUS.md                # Project status
    └── requirements.txt         # Dependencies
    """)

if __name__ == "__main__":
    cleanup_project()
