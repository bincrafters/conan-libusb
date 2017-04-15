"""This script build Conan.io package to multiple platforms."""
from os import getenv
from platform import system
from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.password = getenv("CONAN_PASSWORD")
    builder.add_common_builds(shared_option_name="libusb:shared", pure_c=True)
    if system() == "Windows": # Library not prepared to create a .lib to link with (only dll)
        # Remove shared builds in Windows
        static_builds = []
        for build in builder.builds:
            if not build[1]["libusb:shared"]:
                static_builds.append([build[0], build[1]])
        builder.builds = static_builds
    builder.run()
