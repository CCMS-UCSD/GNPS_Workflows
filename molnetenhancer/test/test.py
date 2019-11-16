import sys
sys.path.insert(0, "../tools/molnetenhancer/")


def testmolnet():
    import molnetenhancer

    #Network Only
    #molnetenhancer.process("047ef85223024f269e44492adc771d9c", None, None, None, None, None, "output")

    #NAP
    #molnetenhancer.process("43c18590ef094c78afaeb7b26f6626d0", None, None, None, None, "6b515b235e0e4c76ba539524c8b4c6d8", "output")

    #Dereplicator
    molnetenhancer.process("2fd31c1651cc41cfbff9d1d473f03cc3", "7a58471f1273400fb5a5379ea1685f77", "bc07013e25584d6f8f022d53eeb2384d", None, None, None, "output")