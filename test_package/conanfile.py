"""Receipt validation for libusb-1.0.21
"""
from os import getenv
from conans import ConanFile, CMake


class TestLibUSBConan(ConanFile):
    """Build test using target package and execute all tests
    """
    channel = getenv("CONAN_CHANNEL", "testing")
    user = getenv("CONAN_USERNAME", "uilianries")
    settings = "os", "compiler", "build_type", "arch"
    requires = "libusb/1.0.21@%s/%s" % (user, channel)
    author = "Uilian Ries <uilianries@gmail.com>"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_dir=self.conanfile_directory, build_dir="./")
        cmake.build()

    def imports(self):
        self.copy(pattern="*.so*", dst="bin", src="lib")
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="FindLibusb1.cmake", dst=".", src=".")

    def test(self):
        cmake = CMake(self)
        cmake.configure(source_dir=self.conanfile_directory, build_dir="./")
        cmake.build()
        cmake.test()
