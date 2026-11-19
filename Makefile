# Run the whole test suite:
#   mutation tests (testers catch the known past bugs),
#   regression tests (fixed generators verify 100%),
#   gate tests (the platform discards unverified questions).
PY ?= .venv/bin/python

.PHONY: test
test:
	$(PY) -m pytest -q tests/
