test-push-full:
	act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 -b

# Caches environment
test-push-fast:
	act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04 -b -r

# Testing individual targets
test-fbmn:
	act -j test-fbmn -P ubuntu-latest=nektos/act-environments-ubuntu:18.04-full -b

test-mshub:
	act -j test-mshub -P ubuntu-latest=nektos/act-environments-ubuntu:18.04-full -b

test-gc-networking:
	act -j test-gc-networking -P ubuntu-latest=nektos/act-environments-ubuntu:18.04-full -b

test-molnet:
	act -j test-molnet -P ubuntu-latest=nektos/act-environments-ubuntu:18.04-full -b