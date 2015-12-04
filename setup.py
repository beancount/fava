from setuptools import setup

setup(name='beancount-web',
      version='0.1.0a1',
      description='A web interface for beancount',
      url='http://github.com/aumayr/beancount-web',
      author='Dominik Aumayr',
      author_email='dominik@aumayr.name',
      license='MIT',
      packages=['beancount_web'],
      install_requires=[
            'beancount',
            'beancount-pygments-lexer',
            'Flask==0.10.1',
            'livereload',
            'Pygments'
      ],
      dependency_links=[
            'hg+https://bitbucket.org/blais/beancount#egg=beancount',
            'git+ssh://git@github.com/aumayr/beancount-pygments-lexer.git#egg=beancount_pygments_lexer'
      ],
      zip_safe=False)
