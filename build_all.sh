#!/bin/sh

python setup.py build sdist
python setup.py build bdist
python setup.py build bdist_wheel
python setup.py build bdist_wheel --universal

