import checker
import sys
if (len(sys.argv) == 2 and sys.argv[1][-4:] == ".odt"):
    check = checker.StyleChecker(sys.argv[1])
    errors = []
    try:
        errors = check.run()
    except Exception:
        print("Файл не существует.")
    for error in errors:
        print (error)
        pass
else:
    print("Файл не был введен или имеет неверное расширение")