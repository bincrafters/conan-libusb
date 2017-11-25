"""Conan receipt package for USB Library 1.0.21
"""
import tempfile
import os
from conans import ConanFile, VisualStudioBuildEnvironment, AutoToolsBuildEnvironment, tools


class LibUSBConan(ConanFile):
    """Download libusb source, build and create package
    """
    name = "libusb"
    version = "1.0.21"
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "enable_udev": [True, False]}
    default_options = "shared=False", "enable_udev=True"
    url = "http://github.com/uilianries/conan-libusb"
    author = "Uilian Ries <uilianries@gmail.com>"
    license = "https://github.com/libusb/libusb/blob/master/COPYING"
    description = "A cross-platform library to access USB devices"
    release_name = "%s-%s" % (name, version)
    install_dir = tempfile.mkdtemp(suffix=name)

    def source(self):
        tools.get("https://github.com/libusb/libusb/releases/download/v%s/%s.tar.bz2" % (self.version, self.release_name))

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.enable_udev

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
        env_build = VisualStudioBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            with tools.chdir(self.release_name):
                solution_file = "libusb_2015.sln"
                if self.settings.compiler.version == "12":
                    solution_file = "libusb_2013.sln"
                elif self.settings.compiler.version == "11":
                    solution_file = "libusb_2012.sln"
                solution_file = os.path.join("msvc", solution_file)
                build_command = tools.build_sln_command(self.settings, solution_file)
                if self.settings.arch == "x86":
                    build_command = build_command.replace("x86", "Win32")
                command = "%s && %s" % (tools.vcvars_command(self.settings), build_command)
                self.run(command)

    def _build_mingw(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        unix_environment = {}
        for key, value in env_build.vars.items():
            unix_environment[key] = value.replace("\\", "/")
        with tools.environment_append(unix_environment):
            configure_args = ['--prefix=%s' % self.install_dir]
            configure_args.append('--enable-shared' if self.options.shared else '--disable-shared')
            configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
            if self.settings.arch == "x86_64":
                configure_args.append('--host=x86_64-w64-mingw32')
            if self.settings.arch == "x86":
                configure_args.append('--build=i686-w64-mingw32')
                configure_args.append('--host=i686-w64-mingw32')
            with tools.chdir(self.release_name):
                tools.run_in_windows_bash(self, tools.unix_path("./configure %s" % ' '.join(configure_args)))
                tools.run_in_windows_bash(self, tools.unix_path("make"))
                tools.run_in_windows_bash(self, tools.unix_path("make install"))

    def _build_macos(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        with tools.environment_append(env_build.vars):
            configure_args = ['--prefix=%s' % self.install_dir]
            with tools.chdir(self.release_name):
                self.run("./configure %s" % ' '.join(configure_args))
                env_build.make(args=["all"])
                env_build.make(args=["install"])

    def _build_linux(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        with tools.environment_append(env_build.vars):
            configure_args = ['--prefix=%s' % self.install_dir]
            configure_args.append('--enable-udev' if self.options.enable_udev else '--disable-udev')
            with tools.chdir(self.release_name):
                env_build.configure(args=configure_args)
                env_build.make(args=["all"])
                env_build.make(args=["install"])

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._build_visual_studio()
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self._build_mingw()
        elif self.settings.os == "Linux":
            self._build_linux()
        else:
            self._build_macos()

    def _package_linux(self):
        self.copy(pattern="*.h", dst="include", src=os.path.join(self.install_dir, "include"))
        self.copy(pattern="*.pc", dst="lib", src=os.path.join(self.install_dir, "lib", "pkgconfig"))
        if self.options.shared:
            self.copy(pattern="*.so*", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
            self.copy(pattern="*.la", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)

    def _package_macos(self):
        self.copy(pattern="*.h", dst="include", src=os.path.join(self.install_dir, "include"))
        if self.options.shared:
            self.copy(pattern="*.dylib", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)

    def _package_visual_studio(self):
        self.copy(pattern="libusb.h", dst=os.path.join("include", "libusb-1.0"), src=os.path.join(self.release_name, "libusb"), keep_path=False)
        arch = "x64" if self.settings.arch == "x86_64" else "Win32"
        source_dir = os.path.join(self.release_name, arch, str(self.settings.build_type), "dll" if self.options.shared else "lib")
        if self.options.shared:
            self.copy(pattern="libusb-1.0.dll", dst="bin", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-1.0.lib", dst="lib", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-usbdk-1.0.dll", dst="bin", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-usbdk-1.0.lib", dst="lib", src=source_dir, keep_path=False)
        else:
            self.copy(pattern="libusb-1.0.lib", dst="lib", src=source_dir, keep_path=False)
            self.copy(pattern="libusb-usbdk-1.0.lib", dst="lib", src=source_dir, keep_path=False)

    def _package_mingw(self):
        self.copy(pattern="*.pc", dst="lib", src=os.path.join(self.install_dir, "lib", "pkgconfig"))
        self.copy(pattern="*.h", dst="include", src=os.path.join(self.install_dir, "include"))
        if self.options.shared:
            self.copy(pattern="*.dll", dst="bin", src=os.path.join(self.install_dir, "bin"), keep_path=False)
            self.copy(pattern="*.dll.a", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        else:
            self.copy(pattern="libusb-1.0.a", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
            self.copy(pattern="*.la", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)

    def package(self):
        self.copy("COPYING", src=self.release_name, dst=".", keep_path=False)
        if self.settings.os == "Linux":
            self._package_linux()
        elif self.settings.os == "Macos":
            self._package_macos()
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._package_visual_studio()
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self._package_mingw()

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
