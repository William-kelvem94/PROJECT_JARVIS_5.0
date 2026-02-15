
try:
    with open('test_results_2.txt', 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        for line in lines:
            if "File" in line or "line" in line or "Error" in line:
                print(line.strip())
except Exception as e:
    print(f"Error reading log: {e}")
