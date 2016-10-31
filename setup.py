from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='prophtools',
      version='1.0',
      description='Python package for general ProphNet prioritization',
      author='Carmen Navarro Luzon',
      long_description=readme(),
      author_email='cnluzon@decsai.ugr.es',
      license='GNU GPLv3',
      packages=['prophtools'],
      install_requires=['scipy', 'numpy', 'networkx', 'sklearn', 'matplotlib'],
      # dependency_links=[],
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Topic :: Bioinformatics :: Network analysis',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=['bin/prophtools'],
      include_package_data=True,
      zip_safe=False)
