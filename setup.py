from setuptools import setup

setup(name='beancount-web',
      version='0.1.0a1',
      description='A web interface for beancount',
      url='http://github.com/aumayr/beancount-web',
      author='Dominik Aumayr',
      author_email='dominik@aumayr.name',
      license='MIT',
      packages=['beancount_web'],
      scripts=['scripts/beancount-web'],
      install_requires=[
            'beancount',
            'beancount-pygments-lexer',
            'Flask==0.10.1',
            'livereload',
            'Pygments'
      ],
      include_package_data=True,
      dependency_links=[
            'hg+https://bitbucket.org/blais/beancount#egg=beancount',
            'git+ssh://git@github.com/aumayr/beancount-pygments-lexer.git#egg=beancount-pygments-lexer'
      ],
      zip_safe=False)
