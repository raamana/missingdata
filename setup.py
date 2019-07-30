#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup
import versioneer

requirements = ['numpy',
                'pandas',
                'xlrd',
                'matplotlib']

setup(
    author="Pradeep Reddy Raamana",
    author_email='raamana@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        ],
    description="missing data visualization and imputation",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description="""missing data visualization and imputation, 
    with blackholes plot""",
    include_package_data=True,
    keywords='missingdata',
    name='missingdata',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(include=['missingdata']),
    setup_requires=requirements,
    test_suite='tests',
    tests_require=requirements,
    url='https://github.com/raamana/missingdata',
    zip_safe=False,
    )
