cmake_minimum_required(VERSION 2.8)

option(WITH_SYSTEM_LIBEVENT "Don't build libevent, use installed" ON)

#set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/cmake/Modules")
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
# Marian
    
#include(ExternalProject)
#set(MARIAN_ROOT "${CMAKE_CURRENT_BINARY_DIR}/marian")
#ExternalProject_Add(marian
#    URL "https://github.com/marian-nmt/marian/archive/master.zip"
#    #URL_MD5 "fcfbd25c03eecde4e4b0dfa58598a426"
#    #CMAKE_ARGS -Wno-dev "-DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>"
#    #add_custom_target(marian COMMAND make run WORKING_DIRECTORY ${MARIAN_ROOT})
#    CONFIGURE_COMMAND "cmake ."
#    BUILD_COMMAND     "make -j 4"
#    INSTALL_DIR ${MARIAN_ROOT}
#)
#set(MARIAN_INCLUDE_DIR ${MARIAN_ROOT}/include)
#set(MARIAN_LIBRARIES ${MARIAN_ROOT}/lib/marian-cpp.a)
#message(STATUS "Found external dependency marian: " ${MARIAN_INCLUDE_DIR})
#include_directories(${MARIAN_INCLUDE_DIR})
#list(APPEND LIBRARIES ${MARIAN_LIBRARIES})
#list(APPEND DEPENDENCIES marian)



########################################################################
add_executable(consumer consumer.cpp)
target_link_libraries(consumer pthread event -lpqxx -lpq ${LIBRARIES})
add_dependencies(consumer ${DEPENDENCIES})
