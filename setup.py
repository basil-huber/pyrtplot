from setuptools import setup

setup(name='pyrtplot',
      version='0.1',
      description='Python Real-time plotting',
      #url='todo',
      author='Basil',
      author_email='basil.huber@gmail.com',
      license='MIT License',
      packages=['pyrtplot','pyrtplot.utils', 'pyrtplot.plotting'],
      install_requires=['numpy', 'matplotlib'],
      zip_safe=False)