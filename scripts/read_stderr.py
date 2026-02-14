
try:
    with open('stderr.txt', 'r', encoding='utf-8', errors='replace') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading stderr.txt: {e}")
