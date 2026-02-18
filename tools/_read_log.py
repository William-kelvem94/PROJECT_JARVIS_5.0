import sys
import re

def clean_text(text):
    # Remove non-ascii
    return re.sub(r'[^\x00-\x7F]+', '?', text)

try:
    filename = sys.argv[1] if len(sys.argv) > 1 else 'data/logs/jarvis_main.log'
    with open(filename, 'rb') as f:
        content = f.read().decode('utf-8', errors='replace')
    
    lines = content.splitlines()[-200:] # Last 200 lines
    
    with open('debug_output.txt', 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(clean_text(line) + '\n')
            
    print("Done")
except Exception as e:
    print(f"Error: {e}")
