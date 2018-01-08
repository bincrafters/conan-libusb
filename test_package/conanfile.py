#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Receipt validation for libusb-1.0.21
"""
import os
from conans import ConanFile, CMake, tools, RunEnvironment


class TestLibUSBConan(ConanFile):
    """Build test using target package and execute all tests
    """
    settings = "os", "compiler", "build_type", "arch", "os_build", "arch_build"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        with tools.environment_append(RunEnvironment(self).vars):
            bin_path = os.path.join("bin", "test_package")
            if self.settings.os == "Windows":
                self.run(bin_path)
            elif self.settings.os == "Macos":
                self.run("DYLD_LIBRARY_PATH=%s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path))
            else:
                self.run("LD_LIBRARY_PATH=%s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path))
