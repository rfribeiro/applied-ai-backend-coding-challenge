cmake_minimum_required(VERSION 2.8)

option(WITH_SYSTEM_LIBEVENT "Don't build libevent, use installed" ON)


add_definitions("-std=c++11")

########################################################################
# RabbitMQ

include(ExternalProject)
set(AMQPCPP_ROOT "${CMAKE_CURRENT_BINARY_DIR}/amqpcpp")
ExternalProject_Add(libamqpcpp
    URL "https://github.com/hoxnox/AMQP-CPP/archive/v2.5.1-nx2.tar.gz"
    URL_MD5 "fcfbd25c03eecde4e4b0dfa58598a426"
    #URL "https://github.com/CopernicaMarketingSoftware/AMQP-CPP/archive/master.zip"
    CMAKE_ARGS -Wno-dev "-DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>"
    INSTALL_DIR ${AMQPCPP_ROOT}
)
set(AMQPCPP_INCLUDE_DIR ${AMQPCPP_ROOT}/include)
set(AMQPCPP_LIBRARIES ${AMQPCPP_ROOT}/lib/libamqp-cpp.a)
message(STATUS "Found external dependency AMQP-CPP: " ${AMQPCPP_INCLUDE_DIR})
include_directories(${AMQPCPP_INCLUDE_DIR})
list(APPEND LIBRARIES ${AMQPCPP_LIBRARIES})
list(APPEND DEPENDENCIES libamqpcpp)

########################################################################
include_directories(${PROJECT_SOURCE_DIR}/inc)
include_directories(${PROJECT_SOURCE_DIR}/src)

add_executable(consumer ${PROJECT_SOURCE_DIR}/src/consumer.cpp)
target_link_libraries(consumer pthread event -lpqxx -lpq ${LIBRARIES})
add_dependencies(consumer ${DEPENDENCIES})
