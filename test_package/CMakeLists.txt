cmake_minimum_required(VERSION 2.8)
project(conan-libusb-test)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

# Conan package ################################################################
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# Source files #################################################################
file(GLOB SOURCE_FILES src/*.c)

# Build application #######################################
add_executable(${PROJECT_NAME} ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

# Add test #####################################################################
enable_testing()
add_test(NAME test-all
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
         COMMAND ${PROJECT_NAME})
