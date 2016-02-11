from setuptools import setup

setup(
    name='beancount-fava',
    version='0.2.0',
    description='A web interface for beancount',
    url='http://github.com/aumayr/fava',
    author='Dominik Aumayr',
    author_email='dominik@aumayr.name',
    license='MIT',
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
        'beancount',
        'Flask==0.10.1',
        'Flask-Assets==0.11',
        'livereload==2.4.1'
    ],
    dependency_links=[
        'hg+https://bitbucket.org/blais/beancount#egg=beancount',
    ],
    zip_safe=False
)
