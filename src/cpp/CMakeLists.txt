cmake_minimum_required(VERSION 2.8)
project(cache)


set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++14 \
    -lpthread -Wall -Werror -Wpedantic")
set(SOURCE_FILES
    test.cpp
    cache.h
    thread_pool.h
)

include_directories(.)
add_executable(cache ${SOURCE_FILES})
