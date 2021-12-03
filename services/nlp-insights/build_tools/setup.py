from __future__ import print_function

from _ast import Or
import configparser
import os
import platform

from setuptools import setup, find_packages
from setuptools.dist import Distribution


class GradleDistribution(Distribution, object):

    excluded_platform_packages = {}

    def __init__(self, attrs):
        config = configparser.ConfigParser()
        configDir = os.path.dirname(os.path.realpath(__file__))

        self.PINNED_TXT = configDir + "/pinned.txt"
        if not os.path.exists(self.PINNED_TXT) or not os.path.exists(
            configDir + "/setup.properties"
        ):
            raise Exception("Files created by ./gradlew build are missing")

        config.read(configDir + "/setup.properties")
        attrs["name"] = config["default"]["project_name"]
        attrs["version"] = config["default"]["project_version"]
        attrs["package_dir"] = {"": config["default"]["project_srcDir"]}
        attrs["packages"] = find_packages(config["default"]["project_srcDir"])
        attrs["install_requires"] = list(self.load_pinned_deps())
        super(GradleDistribution, self).__init__(attrs)

    @property
    def excluded_packages(self):
        platform_name = platform.system().lower()
        if platform_name in self.excluded_platform_packages:
            return set(
                pkg.lower() for pkg in self.excluded_platform_packages[platform_name]
            )
        return set()

    def load_pinned_deps(self):
        blacklisted = self.excluded_packages
        try:
            reqs = []
            with open(self.PINNED_TXT) as fh:
                reqs = fh.readlines()
            # Don't include the version information so that we don't mistakenly
            # introduce a version conflict issue.
            for req in reqs:
                if req:
                    name, version = req.split("==")
                    if name and name.lower() not in blacklisted:
                        yield name
        except IOError:
            raise StopIteration


setup(distclass=GradleDistribution, include_package_data=True)
