from setuptools import setup

setup(name='groundcontrol',
      version='0.1',
      description='Groundcontrol Utilities',
      #url='http://github.com/storborg/funniest',
      author='Basil',
      author_email='basil.huber@flyability.com',
      license='FlyaPrivate',
      packages=['groundcontrol','groundcontrol.utils', 'groundcontrol.plotting'],
      install_requires=['numpy', 'matplotlib'],
      zip_safe=False)