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
    release_name = "%s-%s" % (name, version)
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False] }
    default_options = "shared=True"
    url = "http://github.com/uilianries/conan-libusb"
    author = "Uilian Ries <uilianries@gmail.com>"
    license = "https://github.com/libusb/libusb/blob/master/COPYING"
    description = "A cross-platform library to access USB devices"
    exports = ["CMakeLists.txt", "FindLIBUSB.cmake"]
    install_dir = tempfile.mkdtemp(suffix=name)

    def source(self):
        tar_name = "%s-%s.tar.gz" % (self.name, self.version)
        tools.download("https://github.com/libusb/libusb/releases/download/v%s/%s.tar.bz2" % (self.version, self.release_name), tar_name)
        tools.check_md5(tar_name, "1da9ea3c27b3858fa85c5f4466003e44")
        tools.unzip(tar_name)
        os.unlink(tar_name)
        shutil.copyfile("CMakeLists.txt", os.path.join(self.release_name, "CMakeLists.txt"))

    def system_requirements(self):
        if self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool()
            arch = "i386" if self.settings.arch == "x86" else "amd64"
            package_tool.install(packages="libudev-dev:%s" % arch, update=True)

    def _run_cmd(self, command):
        if self.settings.os == "Windows":
            command = command.replace('\\', '/')
            tools.run_in_windows_bash(self, command)
        else:
            self.run(command)

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            cmake = CMake(self)
            cmake.definitions["WITH_STATIC"] = not self.options.shared or self.settings.compiler == "Visual Studio"
            cmake.definitions["WITH_SHARED"] = self.options.shared
            cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.install_dir
            cmake.configure(source_dir=self.release_name)
            cmake.build()
            cmake.install()
        else:
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = True
            with tools.environment_append(env_build.vars):
                configure_args = ['--prefix=%s' % self.install_dir]
                configure_args.append('--enable-shared' if self.options.shared else '--disable-shared')
                configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
                self._run_cmd("cd %s && ./configure %s" % (self.release_name, ' '.join(configure_args)))
                self._run_cmd("cd %s && make all" % self.release_name)
                self._run_cmd("cd %s && make install" % self.release_name)

    def package(self):
        self.copy("FindLIBUSB.cmake", ".", ".")
        self.copy("COPYING", src=self.release_name, dst=".", keep_path=False)
        self.copy(pattern="*.h", dst="include", src=os.path.join(self.install_dir, "include"))
        self.copy(pattern="*.lib", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=os.path.join(self.install_dir, "lib"), keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=os.path.join(self.install_dir, "lib"), keep_path=False)

    def package_info(self):
        lib_name = 'libusb-1.0' if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio" else 'usb-1.0'
        self.cpp_info.libs.append(lib_name)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
            self.cpp_info.libs.append("udev")
        elif self.settings.os == "Macos":
            self.cpp_info.libs.append("objc")
            self.cpp_info.libs.append("-Wl,-framework,IOKit")
            self.cpp_info.libs.append("-Wl,-framework,CoreFoundation")
