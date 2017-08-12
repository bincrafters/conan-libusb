[![Build Status](https://travis-ci.org/uilianries/conan-libusb.svg?branch=release/1.0.21)](https://travis-ci.org/uilianries/conan-libusb)
[![Build status](https://ci.appveyor.com/api/projects/status/jmc2vnxkb7vkpkwr/branch/release/1.0.21?svg=true)](https://ci.appveyor.com/project/uilianries/conan-libusb/branch/release/1.0.21)
[![License: LGPL v2.1](https://img.shields.io/badge/License-LGPL%20v2.1-blue.svg)](http://www.gnu.org/licenses/lgpl-2.1)
[![Download](https://api.bintray.com/packages/uilianries/conan/libusb%3Auilianries/images/download.svg) ](https://bintray.com/uilianries/conan/libusb%3Auilianries/_latestVersion)

# conan-libusb

![Conan libusb](conan_libusb.png)

# A cross-platform library to access USB devices

[Conan.io](https://conan.io) package for [libusb](http://libusb.info/) project

The packages generated with this **conanfile** can be found in [Bintray](https://bintray.com/uilianries/conan/libusb%3Auilianries).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py

If your are in Windows you should run it from a VisualStudio console in order to get "mc.exe" in path.

## Upload packages to server

    $ conan upload libusb/1.0.21@uilianries/stable --all

## Reuse the packages

### Basic setup

    $ conan install libusb/1.0.21@uilianries/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    libusb/1.0.21@uilianries/stable

    [options]
    libusb:shared=True # False

    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install .

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.

### License
[LGPL-2.1](LICENSE)
