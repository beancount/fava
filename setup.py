import ast
from os import path
import re
from setuptools import find_packages, setup


with open(path.join(path.dirname(__file__), 'fava', '__init__.py'), 'rb') as f:
    VERSION = str(ast.literal_eval(re.search(
        r'__version__\s+=\s+(.*)',
        f.read().decode('utf-8')).group(1)))

with open(path.join(path.dirname(__file__), 'README.rst')) as readme:
    LONG_DESCRIPTION = readme.read()


setup(
    name='fava',
    version=VERSION,
    description='Web interface for the accounting tool Beancount.',
    long_description=LONG_DESCRIPTION,
    url='https://beancount.github.io/fava/',
    author='Dominik Aumayr',
    author_email='dominik@aumayr.name',
    license='MIT',
    keywords='fava beancount accounting',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fava = fava.cli:main',
        ]
    },
    install_requires=[
        'beancount>=2.0b15',
        'click',
        'markdown2>=2.3.0',
        'Flask>=0.10.1',
        'Flask-Babel>=0.10.0',
    ],
    extras_require={
        'excel': [
            'pyexcel>=0.2.2',
            'pyexcel-ods3>=0.1.1',
            'pyexcel-xls>=0.1.0',
            'pyexcel-xlsx>=0.1.0',
        ],
        ':sys_platform == "win32"': [
            'pyreadline'
        ],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
)
