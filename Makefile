.DELETE_ON_ERROR:

all:
	echo "Must specify target."

venv:
	virtualenv venv && sh -c 'source venv/bin/activate'
	pip install -r requirements.txt

clean:
	rm -rf '*.pyc' '*.pyo' build/ .tox/ dist/ *.egg-info   __pycache__
	rm -rf creds.data gcp_reports.json amigo_log.txt

install:
	make clean
	python setup.py install

test:
	pytest

.PHONY: all venv install clean test
