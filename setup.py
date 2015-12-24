import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    requires = filter(None, f.readlines())

with open(os.path.join(here, 'requirements-dev.txt')) as f:
    requires_dev = filter(None, f.readlines())

with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

setup(
    name='mc2',
    version=version,
    description=(
        'Mission Control - allows for easy launching of sites on Marathon'),
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    url='http://github.com/praekelt/mc2',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires_dev,
)
