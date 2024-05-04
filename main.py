import checker
import sys
if (len(sys.argv) == 2 and sys.argv[1][-4:] == ".odt"):
    check = checker.StyleChecker(sys.argv[1])
    for error in check.run():
        print (error)
else:
    print("Файл не был введен или имеет неверное расширение")