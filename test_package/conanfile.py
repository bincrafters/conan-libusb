"""Receipt validation for libusb-1.0.21
"""
from os import getenv
from conans import ConanFile, CMake


class TestLibUSBConan(ConanFile):
    """Build test using target package and execute all tests
    """
    channel = getenv("CONAN_CHANNEL", "testing")
    username = getenv("CONAN_USERNAME", "uilianries")
    settings = "os", "compiler", "build_type", "arch"
    requires = "libusb/1.0.21@%s/%s" % (username, channel)
    generators = "cmake"

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "%s" %s' %
                 (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy(pattern="*.so*", dst="bin", src="lib")

    def test(self):
        self.run("cmake --build . --target test")
