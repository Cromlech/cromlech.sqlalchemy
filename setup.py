from setuptools import setup, find_packages
import os

version = '0.1a1dev'

install_requires = [
    'setuptools',
    'cromlech.io',
    'SQLAlchemy',
    'transaction',
    'zope.interface',
    'zope.component',
    'zope.sqlalchemy',
    ]

tests_require = [
    'pytest',
    ]

setup(name='cromlech.sqlalchemy',
      version=version,
      description="Cromlech Web Framework utility methods and components " +
                  "for application using the SQLAlchemy",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("src", 'cromlech', 'sqlalchemy',
                                         "test_base.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='SQLAlchemy ORM Cromlech',
      author='Dolmen Team',
      author_email='dolmen@list.dolmen-project.org',
      url='http://gitweb.dolmen-project.org',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['cromlech',],
      include_package_data=True,
      zip_safe=False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
