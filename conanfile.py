"""Conan receipt package for USB Library 1.0.21
"""
from os import unlink
from conans import ConanFile
from conans.tools import download
from conans.tools import unzip
from conans.tools import check_md5
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
    options = {"udev": [True, False]}
    default_options = "udev=True"
    url = "http://github.com/uilianries/conan-libusb"
    author = "Uilian Ries <uilianries@gmail.com>"
    license = "https://github.com/libusb/libusb/blob/master/COPYING"
    prefix_install = "%s/_build" % release_name

    def source(self):
        package_name = "%s.tar.bz2" % self.release_name
        url = "https://github.com/libusb/libusb/releases/download/v%s/%s" % (
            self.version, package_name)
        download(url, package_name)
        check_md5(package_name, "1da9ea3c27b3858fa85c5f4466003e44")
        unzip(package_name)
        unlink(package_name)

    def system_requirements(self):
        self.global_system_requirements=True
        if self.settings.os == "Linux":
            self.output.warn("'libudev' library is required in your computer.")
            # (uilianries): Could not possible install i386 and amd64 versions at same time.
            arch = "amd64" if self.settings.arch == "x86_64" else "i386"
            self.run("sudo apt-get install -y libudev-dev:%s || true " % arch)

    def build(self):
        self.prefix_install = "%s/%s/_build" % (self.conanfile_directory, self.release_name)
        env_build = AutoToolsBuildEnvironment(self)
        with environment_append(env_build.vars):
            udev = "--enable-udev" if self.options.udev else "--disable-udev"
            prefix = "--prefix=%s" % self.prefix_install
            self.run("cd %s && ./configure %s %s" % (self.release_name, prefix, udev))
            self.run("cd %s && make" % self.release_name)
            self.run("cd %s && make install" % self.release_name)

    def package(self):
        # Copying headers
        self.copy(
            pattern="*.h",
            dst="include",
            src="%s/include" % self.prefix_install,
            keep_path=True)
        self.copy(
            pattern="*.la",
            dst="lib",
            src="%s/lib" % self.prefix_install,
            keep_path=False)
        self.copy(
            pattern="*.so*",
            dst="lib",
            src="%s/lib" % self.prefix_install,
            keep_path=False)
        self.copy(
            pattern="*.pc",
            dst="lib",
            src="%s/lib" % self.prefix_install,
            keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ['usb-1.0']
