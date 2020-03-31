#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='katka-core',
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description='Katka Django core application',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='D-Nitro',
    author_email='d-nitro@kpn.com',
    url='https://github.com/kpn/katka-core',
    install_requires=[
        'Django>=2.2.9,<3.0',
        'djangorestframework>=3.9.0,<4.0.0',
        'django-encrypted-model-fields>=0.5.8,<1.0.0',
        'drf-nested-routers',
    ],
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
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
