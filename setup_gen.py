#!/usr/bin/env python
import os

from pkgversion import list_requirements, pep440_version, write_setup_py
from setuptools import find_packages

write_setup_py(
    name='katka-core',
    version=os.getenv('tag') or pep440_version(),
    description='Katka Django core application',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='D-Nitro',
    author_email='d-nitro@kpn.com',
    url='https://github.com/kpn/katka-core',
    install_requires=list_requirements('requirements/requirements-base.txt'),
    packages=find_packages(),
    tests_require=['tox'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
