"""Conan receipt package for USB Library 1.0.21
"""
from shutil import copyfile
from tempfile import mkdtemp
from os import unlink
from os.path import join
from conans import ConanFile
from conans import CMake
from conans import AutoToolsBuildEnvironment
from conans.tools import download
from conans.tools import unzip
from conans.tools import chdir
from conans.tools import check_md5
from conans.tools import SystemPackageTool
from conans.tools import environment_append


class LibUSBConan(ConanFile):
    """Download libusb source, build and create package
    """
    name = "libusb"
    version = "1.0.21"
    release_name = "%s-%s" % (name, version)
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False] }
    default_options = "shared=True"
    url = "http://github.com/uilianries/conan-libusb"
    author = "Uilian Ries <uilianries@gmail.com>"
    license = "https://github.com/libusb/libusb/blob/master/COPYING"
    description = "A cross-platform library to access USB devices"
    exports = ["CMakeLists.txt", "FindLibusb1.cmake"]
    build_dir = mkdtemp(suffix=name)

    def source(self):
        tar_name = "%s-%s.tar.gz" % (self.name, self.version)
        download("https://github.com/libusb/libusb/releases/download/v%s/%s.tar.bz2" % (self.version, self.release_name), tar_name)
        check_md5(tar_name, "1da9ea3c27b3858fa85c5f4466003e44")
        unzip(tar_name)
        unlink(tar_name)
        copyfile("CMakeLists.txt", join(self.release_name, "CMakeLists.txt"))

    def system_requirements(self):
        if self.settings.os == "Linux":
            package_tool = SystemPackageTool()
            arch = "i386" if self.settings.arch == "x86" else "amd64"
            package_tool.install(packages="libudev-dev:%s" % arch, update=True)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            cmake = CMake(self)
            cmake.configure(source_dir=self.release_name)
            cmake.build()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = True
            with environment_append(env_build.vars):
                with chdir(self.release_name):
                    shared_option = "--disable-shared" if not self.options.shared else ""
                    self.run("./configure --prefix=%s %s" % (self.build_dir, shared_option))
                    self.run("make")
                    self.run("make install")

    def package(self):
        self.copy("FindLibusb1.cmake", ".", ".")
        self.copy("COPYING", src=self.release_name, dst=".", keep_path=False)
        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="libusb.h", dst=join("include", "libusb-1.0"), src=join(self.release_name, "libusb"))
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
        else:
            self.copy(pattern="*.h", dst="include", src=join(self.build_dir, "include"))
            self.copy(pattern="*.a", dst="lib", src=join(self.build_dir, "lib"))
            self.copy(pattern="*.so*", dst="lib", src=join(self.build_dir, "lib"))
            self.copy(pattern="*.dylib", dst="lib", src=join(self.build_dir, "lib"))

    def package_info(self):
        self.cpp_info.libs = ['usb-1.0']
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            self.cpp_info.libs.append("udev")
        elif self.settings.os == "Macos":
            self.cpp_info.libs.append("objc")
            self.cpp_info.libs.append("-Wl,-framework,IOKit")
            self.cpp_info.libs.append("-Wl,-framework,CoreFoundation")
