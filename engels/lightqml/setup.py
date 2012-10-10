#! /usr/bin/env python

from distutils.core import setup

setup(
    name = "lightqml",
    version = "0.7",
    author = "Fabien Engels",
    author_email = "fabien.engels@unistra.fr",
    description = "A light QML parser",
    url = "https://teatime.u-strasbg.fr/projects/lightqml",
    packages = ('lightqml',),
    package_data = {'lightqml': ['*.xsd']},
)
