import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'blinker',
    ]

setup(name='Pym-elFinder',
      version='0.0',
      description='Pym-elFinder',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        ],
      author='Dirk Makowski',
      author_email='dirk [.] makowski [@] gmail.com',
      url='https://github.com/dmdm/',
      keywords='web ui filemanager javascript widget',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="pym_elfinder_tests",
#      entry_points = """\
#      [console_scripts]
#      """,
      )

