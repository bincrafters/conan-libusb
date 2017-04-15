"""Receipt validation for libusb-1.0.21
"""
from os import getenv
from conans import ConanFile, CMake


class TestLibUSBConan(ConanFile):
    """Build test using target package and execute all tests
    """
    target = "libusb"
    version = "1.0.21"
    name = "%s-test" % target
    channel = getenv("CONAN_CHANNEL", "testing")
    user = getenv("CONAN_USERNAME", "uilianries")
    settings = "os", "compiler", "build_type", "arch"
    requires = "%s/%s@%s/%s" % (target, version, user, channel)
    author = "Uilian Ries <uilianries@gmail.com"
    license = "LGPL-2.1"
    generators = "cmake"

    def build(self):
        cmake = CMake(self.settings)
        cmake.configure(self, source_dir=self.conanfile_directory, build_dir="./")
        cmake.build(self)

    def imports(self):
        self.copy(pattern="*.so*", dst="bin", src="lib")
        self.copy(pattern="*.dll", dst="bin", src="bin")

    def test(self):
        cmake = CMake(self.settings)
        cmake.configure(self, source_dir=self.conanfile_directory, build_dir="./")
        if self.settings.compiler == "Visual Studio":
            self.run("cd bin && conan-libusb-test.exe")
        else:
            cmake.build(self, target="test")