import checker

check = checker.StyleChecker("test.odt")
for error in check.run():
    print (error)