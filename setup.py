import os
import platform
import itertools
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "offlinetb", "__version__.py")) as version_file:
    exec(version_file.read())

_INSTALL_REQUIREMENTS = []
if platform.python_version() < '2.7':
    _INSTALL_REQUIREMENTS.append('unittest2')

setup(name="offlinetb",
      classifiers = [
          "Programming Language :: Python :: 2.7",
          ],
      description="Tools for distilling tracebacks for offline viewing",
      license="BSD",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      url="http://github.com/vmalloc/offlinetb",
      version=__version__,
      packages=find_packages(exclude=["tests"]),
      install_requires=_INSTALL_REQUIREMENTS,
      scripts=[],
      namespace_packages=[]
      )
