cmake_minimum_required(VERSION 3.1)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

# Conan package ################################################################
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# Build application ############################################################
add_executable(${CMAKE_PROJECT_NAME} test_package.c)
set_property(TARGET ${CMAKE_PROJECT_NAME} PROPERTY C_STANDARD 99)
target_link_libraries(${CMAKE_PROJECT_NAME} ${CONAN_LIBS})
