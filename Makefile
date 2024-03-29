.PHONY: test run clean pip-compile

package_name = "countdart"

test:
	pytest

clean:
	rm -rf build/ $(package_name).egg-info
	find -iname "*.pyc" -delete

pip-compile:
	pip-compile pyproject.toml --output-file=requirements/base.txt requirements/base.in --resolver=backtracking
	pip-compile pyproject.toml requirements/test.in --extra=test --output-file=requirements/test.txt --resolver=backtracking
	pip-compile pyproject.toml requirements/dev.in --extra=dev --output-file=requirements/dev.txt --resolver=backtracking
