#!/bin/bash
poetry run coverage run --branch -m pytest
poetry run coverage html
xdg-open htmlcov/index.html
