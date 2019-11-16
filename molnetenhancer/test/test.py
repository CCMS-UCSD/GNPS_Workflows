import sys
sys.path.insert(0, "../tools/molnetenhancer/")


def testmolnet():
    import molnetenhancer

    molnetenhancer.process("047ef85223024f269e44492adc771d9c", None, None, None, None, None, "output")