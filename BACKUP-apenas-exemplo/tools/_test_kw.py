class Test:
    def __init__(self, a, b, c):
        print(a, b, c)

try:
    Test(1, 2, c=3)
    print("Keyword OK")
except Exception as e:
    print("Keyword FAIL:", e)
