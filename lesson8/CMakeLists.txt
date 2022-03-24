cmake_minimum_required(VERSION 3.1)
project(LICM)

# set(CMAKE_C_COMPILER "/opt/homebrew/opt/llvm/bin/clang")
# set(CMAKE_CXX_COMPILER "/opt/homebrew/opt/llvm/bin/clang++")

# support C++14 features used by LLVM 10.0.0
set(CMAKE_CXX_STANDARD 14)

find_package(LLVM REQUIRED CONFIG)
add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})
link_directories(${LLVM_LIBRARY_DIRS})

add_subdirectory(LICM)  # Use your pass name here.
