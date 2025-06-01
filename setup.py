#!/usr/bin/env python3
"""
Setup script to create go2web executable
"""

import os
import stat
import sys
from pathlib import Path

def create_executable():
    """Create go2web executable"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Create the executable content
    executable_content = f"""#!/usr/bin/env python3
import sys
import os

# Add the script directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import and run the main module
from go2web import main

if __name__ == "__main__":
    main()
"""
    
    # Write the executable file
    executable_path = script_dir / "go2web"
    
    with open(executable_path, 'w') as f:
        f.write(executable_content)
    
    # Make it executable
    current_mode = os.stat(executable_path).st_mode
    os.chmod(executable_path, current_mode | stat.S_IEXEC)
    
    print(f"✅ Created executable: {executable_path}")
    print(f"✅ Made file executable")
    
    # Instructions
    print("\n" + "="*50)
    print("SETUP COMPLETE!")
    print("="*50)
    print(f"The go2web executable has been created at: {executable_path}")
    print("\nTo use it:")
    print(f"1. Add to PATH: export PATH=\"{script_dir}:$PATH\"")
    print("2. Or run directly: ./go2web -h")
    print("3. Or use full path:", str(executable_path))
    
    print("\nExamples:")
    print("  ./go2web -h")
    print("  ./go2web -u https://httpbin.org/json")
    print("  ./go2web -s \"python programming\"")

if __name__ == "__main__":
    create_executable()