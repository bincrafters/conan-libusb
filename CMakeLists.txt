cmake_minimum_required(VERSION 3.1)
project(usb)

# Version ######################################################################
set(VERSION_MAJOR 1)
set(VERSION_MINOR 0)
set(VERSION_PATCH 21)

# Project defines ##############################################################
set(TARGET_NAME "${CMAKE_PROJECT_NAME}-${VERSION_MAJOR}.${VERSION_MINOR}")
if (${CMAKE_SYSTEM_NAME} STREQUAL "Darwin")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wl,-framework,IOKit -Wl,-framework,CoreFoundation")
endif()

# Conan ########################################################################
include(../conanbuildinfo.cmake)
conan_basic_setup()

# Include ######################################################################
include_directories(libusb)
include_directories(libusb/os)
if (${CMAKE_SYSTEM_NAME} STREQUAL "Windows")
	include_directories(msvc)
elseif (${CMAKE_SYSTEM_NAME} STREQUAL "Darwin")
	include_directories(Xcode)
elseif (${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
	include_directories(config/${CMAKE_SYSTEM_NAME})
endif()

# Source files #################################################################
file(GLOB SOURCE_FILES libusb/*.c)
if (${CMAKE_SYSTEM_NAME} STREQUAL "Windows")
	file(GLOB PLATFORM_FILES libusb/os/poll_windows.c
	                         libusb/os/threads_windows.c
							 libusb/os/windows_nt_common.c
							 libusb/os/windows_winusb.c
						     libusb/os/windows_usbdk.c)
elseif (${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
	file(GLOB PLATFORM_FILES libusb/os/poll_posix.c
							 libusb/os/threads_posix.c
							 libusb/os/linux_usbfs.c
							 libusb/os/linux_udev.c)
elseif (${CMAKE_SYSTEM_NAME} STREQUAL "Darwin")
	file(GLOB PLATFORM_FILES libusb/os/poll_posix.c
							 libusb/os/threads_posix.c
							 libusb/os/darwin_usb.c)
endif()

# Library list #################################################################
find_package (Threads)
set(TARGET_LIBRARIES "")
if (${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
	set(TARGET_LIBRARIES udev)
elseif (${CMAKE_SYSTEM_NAME} STREQUAL "Darwin")
	set(TARGET_LIBRARIES objc)
endif()

# Build library ################################################################
add_library(${TARGET_NAME} ${SOURCE_FILES} ${PLATFORM_FILES})
target_link_libraries(${TARGET_NAME} ${CMAKE_THREAD_LIBS_INIT} ${TARGET_LIBRARIES})
set_property(TARGET ${TARGET_NAME} PROPERTY C_STANDARD 99)

# Install ######################################################################
install(FILES libusb/libusb.h
    DESTINATION ${CMAKE_INSTALL_PREFIX}/include/${TARGET_NAME})

install(TARGETS ${TARGET_NAME}
        DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)
