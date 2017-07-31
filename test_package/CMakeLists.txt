cmake_minimum_required(VERSION 3.1)
project(conan-libusb-test)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

# Conan package ################################################################
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# Load libusb module ##########################################################
include(${CMAKE_BINARY_DIR}/FindLibusb1.cmake)
find_package(Libusb1 REQUIRED)

# Source files #################################################################
file(GLOB SOURCE_FILES src/*.c)

# Build application #######################################
add_executable(${PROJECT_NAME} ${SOURCE_FILES})
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

# Add test #####################################################################
enable_testing()
add_test(NAME test-all
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
         COMMAND ${PROJECT_NAME})
