test-push-full:
	act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 -b

# Caches environment
test-push-fast:
	act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 -b -r

# Testing individual targets
test-fbmn:
	act -j test-fbmn -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 -b -r

test-mshub:
	act -j test-mshub -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 -b -r

test-gc-networking:
	act -j test-gc-networking -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 -b -r