PYTHON=python
# Windows
# PYTHON=${HOME}/venvs/py312/Scripts/python

.PHONY: usage clean dist testpypi-upload pypi-upload

usage:
	@echo Available make targets are: \
	clean, dist, testpypi-upload, and pypi-upload	

dist:
# Unset PIP_CONFIG_FILE in case pip.conf sets user = True
	env PIP_CONFIG_FILE=/dev/null ${PYTHON} -m build --sdist --wheel .

clean:
	rm -rf build dist */*.egg-info
	rm -rf `find . -name __pycache__`
	rm -f src/_chacha/_chacha.c

testpypi-upload:
	${PYTHON} -m twine upload --verbose --repository testpypi dist/*

pypi-upload:
	${PYTHON} -m twine upload dist/*
