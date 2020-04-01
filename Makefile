test-push:
	act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04

test-fbmn:
	act -j test-fbmn -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 -b
