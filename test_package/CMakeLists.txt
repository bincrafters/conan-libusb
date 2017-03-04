PROJECT(conan-libusb-test)
cmake_minimum_required(VERSION 2.8)

set(CMAKE_VERBOSE_MAKEFILE 1)

# Conan package ###########################################
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# Build application #######################################
add_executable(${PROJECT_NAME} testlibusb.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

# Add test ################################################
enable_testing()
add_test(NAME check
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
         COMMAND ${PROJECT_NAME})
