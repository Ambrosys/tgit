import sys

PY3 = sys.version_info[0] == 3
if not PY3:
    raise RuntimeError("tgit supports python3 only")

import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r'__VERSION__\s+=\s+(.*)')

with open('tgit/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode('utf-8')).group(1)))


def read(fname, split=True):
    with open(fname, 'r') as f:
        content = f.read()
    return content.split('\n') if split else content


setup(
    name='tgit',
    version=version,
    author='Fabian Sandoval Saldias',
    author_email='fabianvss@fineshift.de',
    description="A simple git GUI for tagging commits.",
    license='GPLv3',
    keywords='git tagging',
    url='https://www.github.com/ambrosys/tgit',
    packages=['tgit'],
    install_requires=read('requirements.txt'),
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'tgit = tgit.cli.tgit:main',
            'tgit-show-colors = tgit.cli.show_colors:main',
        ]
    },
)
