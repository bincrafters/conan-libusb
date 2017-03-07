"""This script build Conan.io package to multiple platforms."""
from os import getenv
from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.password = getenv("CONAN_PASSWORD")
    builder.add_common_builds(pure_c=True)
    builder.run()
