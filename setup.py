import ast
import os
import re
from setuptools import setup


with open('fava/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(re.search(
        r'__version__\s+=\s+(.*)',
        f.read().decode('utf-8')).group(1)))


def _read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    return open(path).read()


setup(
    name='beancount-fava',
    version=version,
    description=('A rich web interface for the CL-accounting tool beancount.'),
    long_description=_read('README.rst'),
    url='https://aumayr.github.io/fava/',
    author='Dominik Aumayr',
    author_email='dominik@aumayr.name',
    license='MIT',
    keywords='fava beancount beancount-fava beancount-web'
             'ledger ledger-cli cl-accounting',
    packages=['fava',
              'fava.util',
              'fava.api'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fava = fava.cli:main',
        ]
    },
    install_requires=[
        'beancount>=2.0b12',
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
        ]
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
)
