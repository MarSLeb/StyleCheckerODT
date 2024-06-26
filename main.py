import checker
import sys

if len(sys.argv) == 2 and sys.argv[1][-4:] == ".odt":
    check = checker.StyleChecker(sys.argv[1])
    errors = []
    try:
        errors = check.run()
    except Exception:
        print("Файл не существует.")
    if len(errors) == 0:
        print("все верно")
    else:
        for error in errors:
            print(error.pretty())
else:
    print("Файл не был введен или имеет неверное расширение")