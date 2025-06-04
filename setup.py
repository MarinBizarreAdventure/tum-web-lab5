#!/usr/bin/env python3
"""
Setup script to create go2web executable
Run this script to create the go2web command-line tool
"""

import os
import stat
import sys
import shutil
from pathlib import Path

def create_executable():
    """Create go2web executable"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    print("🚀 Creating go2web executable...")
    print(f"📍 Working directory: {script_dir}")
    print(f"🖥️  Operating System: {'Windows' if os.name == 'nt' else 'Unix/Linux'}")
    
    if os.name == 'nt':  # Windows
        create_windows_executable(script_dir)
    else:  # Unix/Linux/macOS
        create_unix_executable(script_dir)

def create_windows_executable(script_dir):
    """Create Windows executable files"""
    
    # Create .bat file for Windows
    bat_content = f"""@echo off
cd /d "{script_dir}"
python "%~dp0go2web.py" %*
"""
    
    # Create .cmd file (alternative)
    cmd_content = f"""@echo off
cd /d "{script_dir}"
python "%~dp0go2web.py" %*
"""
    
    # Python wrapper script
    py_wrapper = f"""#!/usr/bin/env python3
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
    
    # Write Python wrapper
    py_wrapper_path = script_dir / "go2web.py"
    if not py_wrapper_path.exists():
        with open(py_wrapper_path, 'w') as f:
            f.write(py_wrapper)
        print(f"✅ Created Python wrapper: {py_wrapper_path}")
    
    # Write batch files
    bat_path = script_dir / "go2web.bat"
    with open(bat_path, 'w') as f:
        f.write(bat_content)
    print(f"✅ Created batch file: {bat_path}")
    
    cmd_path = script_dir / "go2web.cmd"
    with open(cmd_path, 'w') as f:
        f.write(cmd_content)
    print(f"✅ Created command file: {cmd_path}")
    
    # Test the executables
    print("\n🧪 Testing executables...")
    try:
        import subprocess
        
        # Test batch file
        result = subprocess.run([str(bat_path), '-h'], 
                              capture_output=True, text=True, timeout=10, 
                              shell=True, cwd=str(script_dir))
        
        if result.returncode == 0:
            print("✅ Batch file test passed!")
        else:
            print(f"⚠️  Batch file test failed: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️  Could not test executable: {e}")
    
    # Instructions for Windows
    print("\n" + "="*60)
    print("🎉 WINDOWS SETUP COMPLETE!")
    print("="*60)
    print("📍 Created executables:")
    print(f"   • {bat_path}")
    print(f"   • {cmd_path}")
    print(f"   • {py_wrapper_path}")
    
    print("\n📋 Usage Options:")
    print("1. Double-click the batch file:")
    print(f"   {bat_path}")
    print("\n2. Run from Command Prompt:")
    print("   go2web.bat -h")
    print("   go2web.cmd -h")
    print("   python go2web.py -h")
    
    print(f"\n3. Add to PATH (optional):")
    print(f"   Add this folder to your PATH: {script_dir}")
    print("   Then you can use: go2web -h")
    
    print("\n🚀 Example Commands:")
    print("   go2web.bat -h")
    print("   go2web.bat -u https://httpbin.org/json")
    print("   go2web.bat -s \"python programming\"")
    
    print("\n💡 Pro Tip:")
    print("   For best experience, open Command Prompt in this folder:")
    print("   Right-click in folder → 'Open in Terminal'")

def create_unix_executable(script_dir):
    """Create Unix/Linux executable"""
    
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
    
    # Test the executable
    print("\n🧪 Testing executable...")
    try:
        import subprocess
        result = subprocess.run([str(executable_path), '-h'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ Executable test passed!")
        else:
            print("⚠️  Executable test failed, but file was created")
    except Exception as e:
        print(f"⚠️  Could not test executable: {e}")
    
    # Instructions for Unix/Linux
    print("\n" + "="*60)
    print("🎉 UNIX/LINUX SETUP COMPLETE!")
    print("="*60)
    print(f"📍 Created executable: {executable_path}")
    
    print("\n📋 Usage Options:")
    print("1. Run directly from current directory:")
    print("   ./go2web -h")
    print(f"2. Add to PATH (optional):")
    print(f"   export PATH=\"{script_dir}:$PATH\"")
    print("   go2web -h")
    print("3. Run with full path:")
    print(f"   {executable_path} -h")
    
    print("\n🚀 Example Commands:")
    print("  ./go2web -h")
    print("  ./go2web -u https://httpbin.org/json")
    print("  ./go2web -s \"python programming\"")

def main():
    """Main setup function"""
    print("🔧 go2web Setup Script")
    print("=" * 30)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Error: Python 3.6 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    try:
        create_executable()
        
        print("\n🧪 Run comprehensive tests:")
        print("  python test.py")
        
        print("\n" + "="*60)
        print("🎯 Next Steps:")
        if os.name == 'nt':
            print("1. Open Command Prompt in this folder")
            print("2. Run: go2web.bat -h")
            print("3. Try: go2web.bat -u https://httpbin.org/json")
        else:
            print("1. Run: ./go2web -h")
            print("2. Try: ./go2web -u https://httpbin.org/json")
        print("3. Test: python test.py")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()