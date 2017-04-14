"""Conan receipt package for USB Library 1.0.21
"""
from tempfile import mkdtemp
from os import unlink
from os.path import join
from conans import ConanFile
from conans.tools import download
from conans.tools import unzip
from conans.tools import check_md5
from conans.tools import chdir
from conans.tools import SystemPackageTool
from conans.tools import environment_append
from conans import AutoToolsBuildEnvironment


class LibUSBConan(ConanFile):
    """Download libusb source, build and create package
    """
    name = "libusb"
    version = "1.0.21"
    release_name = "%s-%s" % (name, version)
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],"udev": [True, False]}
    default_options = "shared=True", "udev=True"
    url = "http://github.com/uilianries/conan-libusb"
    author = "Uilian Ries <uilianries@gmail.com>"
    license = "LGPL-2.1"
    description = "A cross-platform library to access USB devices"
    build_dir = mkdtemp(suffix=name)

    def source(self):
        tar_name = "%s-%s.tar.gz" % (self.name, self.version)
        download("https://github.com/libusb/libusb/releases/download/v%s/%s.tar.bz2" % (self.version, self.release_name), tar_name)
        check_md5(tar_name, "1da9ea3c27b3858fa85c5f4466003e44")
        unzip(tar_name)
        unlink(tar_name)

    def system_requirements(self):
        if self.options.udev and self.settings.os == "Linux":
            package_tool = SystemPackageTool()
            arch = "i386" if self.settings.arch == "x86" else "amd64"
            package_tool.install(packages="libudev-dev:%s" % arch, update=True)

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        with environment_append(env_build.vars):
            with chdir(self.release_name):
                shared_option = "--disable-static" if self.options.shared else "--disable-shared"
                udev_option = "--enable-udev" if self.options.udev else "--disable-udev"
                self.run("./configure --prefix=%s %s %s" % (self.build_dir, shared_option, udev_option))
                self.run("make")
                self.run("make install")

    def package(self):
        self.copy(pattern="*.h", dst="include", src=join(self.build_dir, "include"))
        self.copy(pattern="*.a", dst="lib", src=join(self.build_dir, "lib"))
        self.copy(pattern="*.so*", dst="lib", src=join(self.build_dir, "lib"))
        self.copy(pattern="*.dylib", dst="lib", src=join(self.build_dir, "lib"))

    def package_info(self):
        self.cpp_info.libs = ['usb-1.0']
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            if self.options.udev:
                self.cpp_info.libs.append("udev")
        elif self.settings.os == "Macos":
            self.cpp_info.libs.append("objc")
            self.cpp_info.libs.append("-Wl,-framework,IOKit")
            self.cpp_info.libs.append("-Wl,-framework,CoreFoundation")
