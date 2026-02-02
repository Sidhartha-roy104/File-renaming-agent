# import os
# import subprocess
# from datetime import datetime

# def get_txt_metadata(filepath):
#     """Extract metadata from a text file"""
#     stats = os.stat(filepath)
    
#     # Get file metadata
#     metadata = {
#         "filename": os.path.basename(filepath),
#         "full_path": filepath,
#         "size_bytes": stats.st_size,
#         "size_kb": round(stats.st_size / 1024, 2),
#         "created": datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
#         "modified": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
#         "accessed": datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
#     }
    
#     # Read first few lines of content
#     try:
#         with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
#             content = f.read(500)  # First 500 characters
#             metadata["preview"] = content
#             metadata["line_count"] = len(f.readlines()) + content.count('\n')
#     except:
#         metadata["preview"] = "Could not read content"
#         metadata["line_count"] = 0
    
#     return metadata

# def ask_ollama(prompt):
#     """Send prompt to Ollama"""
#     process = subprocess.Popen(
#         ["ollama", "run", "llama3"],
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#         encoding="utf-8"
#     )
#     stdout, _ = process.communicate(prompt)
#     return stdout.strip()

# def analyze_metadata(filepath):
#     """Main function to analyze file metadata"""
#     print("\n📁 Extracting metadata...\n")
    
#     metadata = get_txt_metadata(filepath)
    
#     # Display metadata
#     print("=" * 60)
#     print("FILE METADATA:")
#     print("=" * 60)
#     for key, value in metadata.items():
#         if key != "preview":
#             print(f"{key.upper()}: {value}")
#     print("=" * 60)
    
#     # Create prompt for Ollama
#     prompt = f"""
# Analyze this text file metadata and provide insights:

# Filename: {metadata['filename']}
# Size: {metadata['size_kb']} KB
# Created: {metadata['created']}
# Last Modified: {metadata['modified']}
# Last Accessed: {metadata['accessed']}

# Content Preview:
# \"\"\"
# {metadata['preview']}
# \"\"\"

# Based on this metadata, answer:
# 1. What type of document is this likely to be?
# 2. Is this file actively being used or is it old/abandoned?
# 3. What can you infer about the content?
# 4. Any recommendations for organizing or naming this file?

# Keep your response concise and clear.
# """
    
#     print("\n🧠 Sending to Ollama for analysis...\n")
    
#     response = ask_ollama(prompt)
    
#     print("=" * 60)
#     print("OLLAMA ANALYSIS:")
#     print("=" * 60)
#     print(response)
#     print("=" * 60)

# if __name__ == "__main__":
#     filepath = input("Enter path to .txt file: ").strip()
    
#     if not os.path.isfile(filepath):
#         print("❌ File not found!")
#     elif not filepath.lower().endswith('.txt'):
#         print("❌ Please provide a .txt file!")
#     else:
#         analyze_metadata(filepath)
#         print("\n✅ Analysis complete!")
import os
import subprocess
from datetime import datetime
import json

# For Windows, we'll use alternate data streams (ADS)
# For cross-platform, we can also create a sidecar JSON file

def get_txt_metadata(filepath):
    """Extract metadata from a text file"""
    stats = os.stat(filepath)
    
    metadata = {
        "filename": os.path.basename(filepath),
        "full_path": filepath,
        "size_bytes": stats.st_size,
        "size_kb": round(stats.st_size / 1024, 2),
        "created": datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
        "modified": datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    # Read content
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1000)
            metadata["preview"] = content
    except:
        metadata["preview"] = "Could not read content"
    
    return metadata

def ask_ollama(prompt):
    """Send prompt to Ollama"""
    process = subprocess.Popen(
        ["ollama", "run", "llama3"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )
    stdout, _ = process.communicate(prompt)
    return stdout.strip()

def write_metadata_to_ads(filepath, description):
    """Write metadata using Windows Alternate Data Stream"""
    try:
        ads_path = f"{filepath}:description.txt"
        with open(ads_path, 'w', encoding='utf-8') as f:
            f.write(description)
        print(f"✅ Metadata written to ADS: {ads_path}")
        return True
    except Exception as e:
        print(f"⚠️ Could not write to ADS: {e}")
        return False

def write_metadata_to_sidecar(filepath, description, metadata):
    """Write metadata to a companion JSON file"""
    base = os.path.splitext(filepath)[0]
    meta_file = f"{base}.meta.json"
    
    meta_data = {
        "original_file": os.path.basename(filepath),
        "description": description,
        "analyzed_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "file_metadata": metadata
    }
    
    try:
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, indent=2)
        print(f"✅ Metadata saved to: {meta_file}")
        return True
    except Exception as e:
        print(f"❌ Could not write sidecar file: {e}")
        return False

def read_metadata_from_ads(filepath):
    """Read metadata from Windows ADS"""
    try:
        ads_path = f"{filepath}:description.txt"
        with open(ads_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def read_metadata_from_sidecar(filepath):
    """Read metadata from sidecar JSON file"""
    base = os.path.splitext(filepath)[0]
    meta_file = f"{base}.meta.json"
    
    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def analyze_and_save_metadata(filepath, method="both"):
    """Main function to analyze file and save metadata"""
    print("\n📁 Extracting file information...\n")
    
    metadata = get_txt_metadata(filepath)
    
    # Display metadata
    print("=" * 60)
    print("FILE METADATA:")
    print("=" * 60)
    for key, value in metadata.items():
        if key != "preview":
            print(f"{key.upper()}: {value}")
    print("=" * 60)
    
    # Create prompt for Ollama
    prompt = f"""
Analyze this text file and provide a concise description (2-3 sentences max):

Filename: {metadata['filename']}
Content Preview:
\"\"\"
{metadata['preview']}
\"\"\"

Provide ONLY a brief description of what this file contains. No analysis, no recommendations - just describe the content.
"""
    
    print("\n🧠 Generating description with Ollama...\n")
    
    description = ask_ollama(prompt)
    
    print("=" * 60)
    print("GENERATED DESCRIPTION:")
    print("=" * 60)
    print(description)
    print("=" * 60)
    
    # Save metadata
    print("\n💾 Saving metadata...\n")
    
    if method in ["ads", "both"]:
        write_metadata_to_ads(filepath, description)
    
    if method in ["sidecar", "both"]:
        write_metadata_to_sidecar(filepath, description, metadata)
    
    return description

def view_saved_metadata(filepath):
    """View previously saved metadata"""
    print("\n🔍 Checking for saved metadata...\n")
    
    # Check ADS
    ads_desc = read_metadata_from_ads(filepath)
    if ads_desc:
        print("=" * 60)
        print("METADATA FROM ADS:")
        print("=" * 60)
        print(ads_desc)
        print("=" * 60)
    
    # Check sidecar
    sidecar_data = read_metadata_from_sidecar(filepath)
    if sidecar_data:
        print("\n" + "=" * 60)
        print("METADATA FROM SIDECAR FILE:")
        print("=" * 60)
        print(json.dumps(sidecar_data, indent=2))
        print("=" * 60)
    
    if not ads_desc and not sidecar_data:
        print("❌ No saved metadata found for this file.")

if __name__ == "__main__":
    print("=" * 60)
    print("  TXT FILE METADATA MANAGER")
    print("=" * 60)
    print("\n1. Analyze and add description to file")
    print("2. View saved metadata")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    filepath = input("Enter path to .txt file: ").strip()
    
    if not os.path.isfile(filepath):
        print("❌ File not found!")
    elif not filepath.lower().endswith('.txt'):
        print("❌ Please provide a .txt file!")
    else:
        if choice == "1":
            print("\nMetadata storage method:")
            print("1. ADS (Windows Alternate Data Stream - hidden)")
            print("2. Sidecar JSON file (visible .meta.json file)")
            print("3. Both")
            
            method_choice = input("\nEnter choice (1/2/3): ").strip()
            method_map = {"1": "ads", "2": "sidecar", "3": "both"}
            method = method_map.get(method_choice, "both")
            
            analyze_and_save_metadata(filepath, method)
            print("\n✅ Process complete!")
            
        elif choice == "2":
            view_saved_metadata(filepath)
        else:
            print("❌ Invalid choice!")