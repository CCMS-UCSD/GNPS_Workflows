import sys
sys.path.insert(0, "../tools/molnetenhancer/")


def testmolnet():
    import molnetenhancer

    #Network Only
    molnetenhancer.process("047ef85223024f269e44492adc771d9c", "output")

    #NAP
    molnetenhancer.process("43c18590ef094c78afaeb7b26f6626d0", "output", nap_job_id="6b515b235e0e4c76ba539524c8b4c6d8")

    #Dereplicator
    molnetenhancer.process("2fd31c1651cc41cfbff9d1d473f03cc3", "output", dereplicator_job_id="bc07013e25584d6f8f022d53eeb2384d", varquest_job_id="7a58471f1273400fb5a5379ea1685f77")
    
    #Expected failed dereplicator
    molnetenhancer.process("a3587fd252294c248cc1839d97109edc", "output", dereplicator_job_id="612f3ad9841a466f81e802ea2df3cc2f")