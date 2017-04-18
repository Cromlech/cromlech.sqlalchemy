from setuptools import setup, find_packages
import os

version = '0.3b1'

install_requires = [
    'setuptools',
    'SQLAlchemy',
    'transaction >= 1.2',
    'zope.interface',
    'zope.sqlalchemy >= 0.7',
    ]

tests_require = [
    ]

setup(name='cromlech.sqlalchemy',
      version=version,
      description="Cromlech Web Framework utility methods and components " +
                  "for applications based on SQLAlchemy.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("src", 'cromlech', 'sqlalchemy',
                                         "test_api.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='SQLAlchemy ORM Cromlech',
      author='Dolmen Team',
      author_email='dolmen@list.dolmen-project.org',
      url='http://gitweb.dolmen-project.org',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['cromlech', ],
      include_package_data=True,
      zip_safe=False,
      tests_require=tests_require,
      install_requires=install_requires,
      extras_require={'test': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
