
import os
import codecs

TARGET_DIR = os.path.join(os.path.dirname(__file__), "..", "src")
EXTENSIONS = (".py",)

def remove_bom_from_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check for BOM
        if content.startswith(codecs.BOM_UTF8):
            clean_content = content[len(codecs.BOM_UTF8):]
            with open(file_path, 'wb') as f:
                f.write(clean_content)
            print(f"[FIXED] Removed BOM from: {file_path}")
            return True
        else:
            # print(f"[OK] No BOM in: {file_path}")
            return False
    except Exception as e:
        print(f"[ERROR] processing {file_path}: {e}")
        return False

def main():
    print("=== JARVIS 5.0 BOM REMOVAL TOOL ===")
    print(f"Targeting: {TARGET_DIR}")
    
    count = 0
    fixed_count = 0
    
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(EXTENSIONS):
                path = os.path.join(root, file)
                count += 1
                if remove_bom_from_file(path):
                    fixed_count += 1
                    
    print("-" * 30)
    print(f"Scanned {count} files.")
    print(f"Fixed {fixed_count} files.")
    print("Done.")

if __name__ == "__main__":
    main()
