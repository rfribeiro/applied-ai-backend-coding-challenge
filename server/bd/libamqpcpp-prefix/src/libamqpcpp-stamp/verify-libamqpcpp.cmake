set(file "/home/rafael/Projects/flask_recipe_app_new/server/bd/libamqpcpp-prefix/src/v2.5.1-nx2.tar.gz")
message(STATUS "verifying file...
     file='${file}'")
set(expect_value "fcfbd25c03eecde4e4b0dfa58598a426")
set(attempt 0)
set(succeeded 0)
while(${attempt} LESS 3 OR ${attempt} EQUAL 3 AND NOT ${succeeded})
  file(MD5 "${file}" actual_value)
  if("${actual_value}" STREQUAL "${expect_value}")
    set(succeeded 1)
  elseif(${attempt} LESS 3)
    message(STATUS "MD5 hash of ${file}
does not match expected value
  expected: ${expect_value}
    actual: ${actual_value}
Retrying download.
")
    file(REMOVE "${file}")
    execute_process(COMMAND ${CMAKE_COMMAND} -P "/home/rafael/Projects/flask_recipe_app_new/server/bd/libamqpcpp-prefix/src/libamqpcpp-stamp/download-libamqpcpp.cmake")
  endif()
  math(EXPR attempt "${attempt} + 1")
endwhile()

if(${succeeded})
  message(STATUS "verifying file... done")
else()
  message(FATAL_ERROR "error: MD5 hash of
  ${file}
does not match expected value
  expected: ${expect_value}
    actual: ${actual_value}
")
endif()
