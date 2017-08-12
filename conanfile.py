"""Conan receipt package for USB Library 1.0.21
"""
import shutil
import tempfile
import os
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools


class LibUSBConan(ConanFile):
    """Download libusb source, build and create package
    """
    name = "libusb"
    version = "1.0.21"
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "enable_udev": [True, False], "enable_usbdk": [True, False]}
    default_options = "shared=True", "enable_udev=True", "enable_usbdk=False"
    url = "http://github.com/uilianries/conan-libusb"
    author = "Uilian Ries <uilianries@gmail.com>"
    license = "https://github.com/libusb/libusb/blob/master/COPYING"
    description = "A cross-platform library to access USB devices"
    exports_sources = ["CMakeLists.txt", "FindLIBUSB.cmake"]
    release_name = "%s-%s" % (name, version)
    install_dir = tempfile.mkdtemp(suffix=name)

    def source(self):
        tools.get("https://github.com/libusb/libusb/releases/download/v%s/%s.tar.bz2" % (self.version, self.release_name))
        shutil.copyfile("CMakeLists.txt", os.path.join(self.release_name, "CMakeLists.txt"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.enable_udev
        elif self.settings.os == "Linux":
            del self.options.enable_usbdk

    def system_requirements(self):
        # TODO: libudev could be moved to a package
        if self.settings.os == "Linux":
            if self.options.enable_udev:
                package_tool = tools.SystemPackageTool()
                arch = "i386" if self.settings.arch == "x86" else "amd64"
                package_tool.install(packages="libudev-dev:%s" % arch, update=True)

    def _build_visual_studio(self):
        cmake = CMake(self)
        cmake.definitions["WITH_SHARED"] = self.options.shared
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.install_dir
        cmake.configure(source_dir=self.release_name)
        cmake.build()
        cmake.install()

    def _build_mingw(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        # Solve Windows path on MingW
        unix_environment = {}
        for key, value in env_build.vars.items():
            unix_environment[key] = value.replace("\\", "/")
        with tools.environment_append(unix_environment):
            configure_args = ['--prefix=%s' % self.install_dir]
            configure_args.append('--enable-usbdk' if self.options.enable_usbdk else '--disable-usbdk')
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
            configure_args.append('--enable-shared' if self.options.shared else '--disable-shared')
            configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
            with tools.chdir(self.release_name):
                self.run("./configure %s" % ' '.join(configure_args))
                env_build.make(args=["all"])
                env_build.make(args=["install"])

    def _build_linux(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        with tools.environment_append(env_build.vars):
            configure_args = ['--prefix=%s' % self.install_dir]
            configure_args.append('--enable-shared' if self.options.shared else '--disable-shared')
            configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
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

    def package(self):
        self.copy("FindLIBUSB.cmake", ".", ".")
        self.copy("COPYING", src=self.release_name, dst=".", keep_path=False)
        self.copy(pattern="*.h", dst="include", src=os.path.join(self.install_dir, "include"))
        self.copy(pattern="*.pc", dst="lib", src=os.path.join(self.install_dir, "lib", "pkgconfig"))
        self.copy(pattern="*.lib", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=os.path.join(self.install_dir, "bin"), keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.la", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)

    def package_info(self):
        lib_name = 'libusb-1.0' if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio" else 'usb-1.0'
        self.cpp_info.libs.append(lib_name)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            if self.options.enable_udev:
                self.cpp_info.libs.append("udev")
        elif self.settings.os == "Macos":
            self.cpp_info.libs.append("objc")
            self.cpp_info.libs.append("-Wl,-framework,IOKit")
            self.cpp_info.libs.append("-Wl,-framework,CoreFoundation")
