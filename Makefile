.PHONY: clean dist gen

clean:
	$(info Cleaning .pyc and __pycache__ files)
	$(shell find . -name "*.pyc" -o -name "__pycache__" -o -name ".DS_Store" | xargs rm -rf)

dist: clean
	mkdir -p dist
	rm -rf dist/*
	zip -r dist/search.`git rev-parse --short HEAD`.zip client data server tests README.md requirements.txt runserver.py THOUGHTS.md
gen:
	cd generator
	python generator.py
