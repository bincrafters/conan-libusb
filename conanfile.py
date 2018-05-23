#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Conan receipt package for USB Library
"""
import os
from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools


class LibUSBConan(ConanFile):
    """Download libusb source, build and create package
    """
    name = "libusb"
    version = "1.0.21"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "enable_udev": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "enable_udev=True", "fPIC=True"
    homepage = "https://github.com/libusb/libusb"
    url = "http://github.com/bincrafters/conan-libusb"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "GPL-2"
    description = "A cross-platform library to access USB devices"
    source_subfolder = "source_subfolder"
    exports = ["LICENSE.md"]

    def source(self):
        release_name = "%s-%s" % (self.name, self.version)
        tools.get("{0}/releases/download/v{1}/{2}.tar.bz2".format(self.homepage, self.version, release_name))
        os.rename(release_name, self.source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.enable_udev
        if self.settings.os == "Windows":
            del self.options.fPIC

    def system_requirements(self):
        if self.settings.os == "Linux":
            if self.options.enable_udev:
                package_tool = tools.SystemPackageTool()
                libudev_name = ""
                os_info = tools.OSInfo()
                if os_info.with_apt:
                    libudev_name = "libudev-dev"
                    if tools.detected_architecture() == "x86_64" and str(self.settings.arch) == "x86":
                        libudev_name += ":i386"
                    elif "x86" in tools.detected_architecture() and "arm" in str(self.settings.arch):
                        libudev_name += ":armhf"
                elif os_info.with_yum:
                    libudev_name = "libudev-devel"
                    if tools.detected_architecture() == "x86_64" and str(self.settings.arch) == "x86":
                        libudev_name += ".i686"
                else:
                    raise Exception("Could not install libudev: Undefined package name for platform.")
                package_tool.install(packages=libudev_name, update=True)

    def _build_visual_studio(self):
        with tools.chdir(self.source_subfolder):
            solution_file = "libusb_2015.sln"
            if self.settings.compiler.version == "12":
                solution_file = "libusb_2013.sln"
            elif self.settings.compiler.version == "11":
                solution_file = "libusb_2012.sln"
            solution_file = os.path.join("msvc", solution_file)
            platforms = {"x86":"Win32"}
            msbuild = MSBuild(self)
            msbuild.build(solution_file, platforms=platforms, upgrade_project=False)

    def _build_mingw(self):
        env_build = AutoToolsBuildEnvironment(self, win_bash=True)
        configure_args = ['--prefix="%s"' % self.package_folder]
        configure_args.append('--enable-shared' if self.options.shared else '--disable-shared')
        configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
        if self.settings.arch == "x86_64":
            configure_args.append('--host=x86_64-w64-mingw32')
        if self.settings.arch == "x86":
            configure_args.append('--build=i686-w64-mingw32')
            configure_args.append('--host=i686-w64-mingw32')
        with tools.chdir(self.source_subfolder):
            env_build.configure(args=configure_args)
            env_build.make()
            env_build.make(args=["install"])

    def _build_unix(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = self.options.fPIC
        configure_args = None
        if self.settings.os == "Linux":
            configure_args = ['--enable-udev' if self.options.enable_udev else '--disable-udev']
        with tools.chdir(self.source_subfolder):
            env_build.configure(args=configure_args)
            env_build.make(args=["all"])
            env_build.make(args=["install"])

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._build_visual_studio()
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self._build_mingw()
        else:
            self._build_unix()

    def _package_visual_studio(self):
        self.copy(pattern="libusb.h", dst=os.path.join("include", "libusb-1.0"), src=os.path.join(self.source_subfolder, "libusb"), keep_path=False)
        arch = "x64" if self.settings.arch == "x86_64" else "Win32"
        source_dir = os.path.join(self.source_subfolder, arch, str(self.settings.build_type), "dll" if self.options.shared else "lib")
        if self.options.shared:
            self.copy(pattern="libusb-1.0.dll", dst="bin", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-1.0.lib", dst="lib", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-usbdk-1.0.dll", dst="bin", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-usbdk-1.0.lib", dst="lib", src=source_dir, keep_path=False)
        else:
            self.copy(pattern="libusb-1.0.lib", dst="lib", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-usbdk-1.0.lib", dst="lib", src=source_dir, keep_path=False)

    def package(self):
        self.copy("COPYING", src=self.source_subfolder, dst="licenses", keep_path=False)
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._package_visual_studio()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            if self.options.enable_udev:
                self.cpp_info.libs.append("udev")
        elif self.settings.os == "Macos":
            self.cpp_info.libs.append("objc")
            self.cpp_info.libs.append("-Wl,-framework,IOKit")
            self.cpp_info.libs.append("-Wl,-framework,CoreFoundation")
