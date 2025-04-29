***********
Development
***********

To recreate the development environment::

	conda create -n xmlhelper python==3.13
	conda activate xmlhelper
	python -m pip install -e .
	python -m pip install Sphinx
	python -m pip install coverage

Run doctests with ``coverage run test.py``.
Aim for 100% coverage.

Create the documentation with ``make html`` in ``doc``.
