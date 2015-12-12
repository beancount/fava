from setuptools import setup

setup(name='beancount-web',
      version='0.1.0a1',
      description='A web interface for beancount',
      url='http://github.com/aumayr/beancount-web',
      author='Dominik Aumayr',
      author_email='dominik@aumayr.name',
      license='MIT',
      packages=['beancount_web'],
      entry_points={
          'console_scripts': [
              'beancount-web = beancount_web.cli:main',
          ]
      },
      install_requires=[
            'beancount',
            'Flask==0.10.1',
            'livereload',
            'Pygments'
      ],
      include_package_data=True,
      dependency_links=[
            'hg+https://bitbucket.org/blais/beancount#egg=beancount',
      ],
      zip_safe=False)
