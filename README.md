[![Build Status](https://travis-ci.org/bincrafters/conan-libusb.svg?branch=release/1.0.21)](https://travis-ci.org/bincrafters/conan-libusb)
[![Build status](https://ci.appveyor.com/api/projects/status/redftqwgxxssmtwf/branch/stable/1.0.21?svg=true)](https://ci.appveyor.com/project/BinCrafters/conan-libusb/branch/stable/1.0.21)
[![License: LGPL v2.1](https://img.shields.io/badge/License-LGPL%20v2.1-blue.svg)](http://www.gnu.org/licenses/lgpl-2.1)
[![Download](https://api.bintray.com/packages/bincrafters/publi-conan/libpcap%3Abincrafters/images/download.svg?version=1.0.21%3Astable)](https://bintray.com/bincrafters/conan/libpcap%3Abincrafters/1.8.1%3Astable/link)

# conan-libusb

![Conan libusb](conan_libusb.png)

# A cross-platform library to access USB devices

[Conan.io](https://conan.io) package for [libusb](http://libusb.info/) project

The packages generated with this **conanfile** can be found in [Bintray](https://bintray.com/bincrafters/public-conan/libusb%3Abincrafters).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py

If your are in Windows you should run it from a VisualStudio console in order to get "mc.exe" in path.

## Upload packages to server

    $ conan upload libusb/1.0.21@bincrafters/stable --all

## Reuse the packages

### Basic setup

    $ conan install libusb/1.0.21@bincrafters/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    libusb/1.0.21@bincrafters/stable

    [options]
    libusb:shared=True # False
    enable_udev=True # False

    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install .

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.

### License
[LGPL-2.1](LICENSE)
