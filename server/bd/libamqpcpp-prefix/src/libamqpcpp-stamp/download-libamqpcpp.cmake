if(EXISTS "/home/rafael/Projects/flask_recipe_app_new/server/bd/libamqpcpp-prefix/src/v2.5.1-nx2.tar.gz")
  file("MD5" "/home/rafael/Projects/flask_recipe_app_new/server/bd/libamqpcpp-prefix/src/v2.5.1-nx2.tar.gz" hash_value)
  if("x${hash_value}" STREQUAL "xfcfbd25c03eecde4e4b0dfa58598a426")
    return()
  endif()
endif()
message(STATUS "downloading...
     src='https://github.com/hoxnox/AMQP-CPP/archive/v2.5.1-nx2.tar.gz'
     dst='/home/rafael/Projects/flask_recipe_app_new/server/bd/libamqpcpp-prefix/src/v2.5.1-nx2.tar.gz'
     timeout='none'")




file(DOWNLOAD
  "https://github.com/hoxnox/AMQP-CPP/archive/v2.5.1-nx2.tar.gz"
  "/home/rafael/Projects/flask_recipe_app_new/server/bd/libamqpcpp-prefix/src/v2.5.1-nx2.tar.gz"
  SHOW_PROGRESS
  # no TIMEOUT
  STATUS status
  LOG log)

list(GET status 0 status_code)
list(GET status 1 status_string)

if(NOT status_code EQUAL 0)
  message(FATAL_ERROR "error: downloading 'https://github.com/hoxnox/AMQP-CPP/archive/v2.5.1-nx2.tar.gz' failed
  status_code: ${status_code}
  status_string: ${status_string}
  log: ${log}
")
endif()

message(STATUS "downloading... done")
