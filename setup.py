import os
from setuptools import setup

version = __import__('fava').__version__
author  = __import__('fava').__author__
author_email  = __import__('fava').__author_email__
url     = __import__('fava').__url__
license = __import__('fava').__license__

read_md = lambda fname: open(os.path.join(os.path.dirname(__file__), fname), 'r').read()

setup(
    name='beancount-fava',
    version=version,
    description=('A rich web interface for the CL-accounting tool beancount.'),
    long_description=read_md('README.rst'),
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    keywords='fava beancount beancount-fava beancount-web ledger ledger-cli cl-accounting',
    packages=['fava',
              'fava.util',
              'fava.api'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fava = fava.cli:main',
            'beancount-web = fava.cli:main',
        ]
    },
    install_requires=[
        'beancount>=2.0b6',
        'pygments>=2.1.1',
        'beancount-pygments-lexer>=0.1.2',
        'markdown2>=2.3.0',
        'Flask>=0.10.1',
        'livereload>=2.4.1',
        'pyexcel>=0.2.0',
        'pyexcel-ods3>=0.1.1',
        'pyexcel-xls>=0.1.0',
        'pyexcel-xlsx>=0.1.0'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
)
