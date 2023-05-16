#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'gitpython', 'python-frontmatter'
]

test_requirements = [ ]

setup(
    author="Nikolas Siccha",
    author_email='nikolassiccha@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Extracts versioned quarto notebook snapshots from the git commit history.",
    entry_points={
        'console_scripts': [
            'quarto_snapshots=quarto_snapshots:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='quarto_snapshots',
    name='quarto_snapshots',
    packages=find_packages(include=['quarto_snapshots', 'quarto_snapshots.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/nsiccha/quarto_snapshots',
    version='0.1.0',
    zip_safe=False,
)
