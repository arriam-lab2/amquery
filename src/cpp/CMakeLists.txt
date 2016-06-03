cmake_minimum_required(VERSION 2.8)
project(cache)

set(Boost_USE_MULTITHREADED ON)
find_package(Boost REQUIRED)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} --std=c++14 -lboost_system \
    -lboost_thread -Wall -Werror -Wpedantic -g")
set(SOURCE_FILES
    test.cpp
    cache.h
    thread_pool.h
)

if(Boost_FOUND)
    include_directories(. ${Boost_INCLUDE_DIR})
    add_executable(cache ${SOURCE_FILES})
    target_link_libraries(cache ${Boost_LIBRARIES})
endif()
