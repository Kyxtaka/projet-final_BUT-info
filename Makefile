MODULE_TEST=tests

.PHONY: tests
tests:
        python -m pytest ${MODULE_TEST}

.PHONY: coverage
coverage:
        python -m coverage run -m unittest
        python -m coverage report
		
.PHONY: clean
clean:
        find . -type f -name "*.pyc" | xargs rm -fr
        find . -type d -name __pycache__ | xargs rm -fr

