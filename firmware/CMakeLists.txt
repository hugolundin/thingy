##########################################################################
# "THE ANY BEVERAGE-WARE LICENSE" (Revision 42 - based on beer-ware
# license):
# <dev@layer128.net> wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and
# you think this stuff is worth it, you can buy me a be(ve)er(age) in
# return. (I don't like beer much.)
#
# Matthias Kleemann
# (Modified by Hugo Lundin, 2021)
##########################################################################

cmake_minimum_required(VERSION 3.21)

set (CMAKE_EXPORT_COMPILE_COMMANDS ON)
message(STATUS "Set CMAKE_EXPORT_COMPILE_COMMANDS to ${CMAKE_EXPORT_COMPILE_COMMANDS}")

### TOOLCHAIN SETUP AREA #################################################
# Set any variables used in the toolchain prior project() call. In that
# case they are already set and used.
##########################################################################

##########################################################################
# tools to beused for programming the AVR
##########################################################################
set(AVR_UPLOADTOOL avrdude)
set(AVR_PROGRAMMER avrispmkII)
set(AVR_UPLOADTOOL_PORT usb)

##########################################################################
# AVR and fuses needs to be set
##########################################################################
set(AVR_MCU atmega328)
set(AVR_H_FUSE 0xd9)
set(AVR_L_FUSE 0xc3)

##########################################################################
# Toolchain
##########################################################################

set(CMAKE_TOOLCHAIN_FILE "${CMAKE_SOURCE_DIR}/Meta/CMake/generic-gcc-avr.cmake")
message(STATUS "Set CMAKE_TOOLCHAIN_FILE to ${CMAKE_TOOLCHAIN_FILE}")

### END TOOLCHAIN SETUP AREA #############################################

# Intentionally left blank, due to a different approach of using the
# toolchain file via -DCMAKE_TOOLCHAIN_FILE=path/to/generic-gcc-avr.cmake
# at the cmake command line call

##########################################################################
# name your project
##########################################################################

project(THINGY C)
set(CMAKE_C_STANDARD 99)

##########################################################################
# status messages
##########################################################################
message(STATUS "Current uploadtool is: ${AVR_UPLOADTOOL}")
message(STATUS "Current programmer is: ${AVR_PROGRAMMER}")
message(STATUS "Current upload port is: ${AVR_UPLOADTOOL_PORT}")
message(STATUS "Current uploadtool options are: ${AVR_UPLOADTOOL_OPTIONS}")
message(STATUS "Current MCU is set to: ${AVR_MCU}")
message(STATUS "Current H_FUSE is set to: ${AVR_H_FUSE}")
message(STATUS "Current L_FUSE is set to: ${AVR_L_FUSE}")

##########################################################################
# set build type
##########################################################################
#if(NOT CMAKE_BUILD_TYPE)
   set(CMAKE_BUILD_TYPE Debug)
#endif(NOT CMAKE_BUILD_TYPE)

##########################################################################
# needs to be defined for AVR toolchain
##########################################################################
set(MCU_SPEED "4000000UL")

##########################################################################
# some cmake cross-compile necessities
##########################################################################

if(DEFINED ENV{AVR_FIND_ROOT_PATH})
    set(CMAKE_FIND_ROOT_PATH $ENV{AVR_FIND_ROOT_PATH})
else(DEFINED ENV{AVR_FIND_ROOT_PATH})
    if(EXISTS "/opt/local/avr")
      set(CMAKE_FIND_ROOT_PATH "/opt/local/avr")
    elseif(EXISTS "/usr/avr")
      set(CMAKE_FIND_ROOT_PATH "/usr/avr")
    elseif(EXISTS "/usr/lib/avr")
      set(CMAKE_FIND_ROOT_PATH "/usr/lib/avr")
    elseif(EXISTS "/usr/local/CrossPack-AVR")
      set(CMAKE_FIND_ROOT_PATH "/usr/local/CrossPack-AVR")
    elseif(EXISTS "/usr/local/opt/avr-gcc")
      set(CMAKE_FIND_ROOT_PATH "/usr/local/opt/avr-gcc")
    else(EXISTS "/opt/local/avr")
      message(FATAL_ERROR "Please set AVR_FIND_ROOT_PATH in your environment.")
    endif(EXISTS "/opt/local/avr")
endif(DEFINED ENV{AVR_FIND_ROOT_PATH})
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
# not added automatically, since CMAKE_SYSTEM_NAME is "generic"
set(CMAKE_SYSTEM_INCLUDE_PATH "${CMAKE_FIND_ROOT_PATH}/include")
set(CMAKE_SYSTEM_LIBRARY_PATH "${CMAKE_FIND_ROOT_PATH}/lib")

##########################################################################
# status messages for generating
##########################################################################
message(STATUS "Set CMAKE_FIND_ROOT_PATH to ${CMAKE_FIND_ROOT_PATH}")
message(STATUS "Set CMAKE_SYSTEM_INCLUDE_PATH to ${CMAKE_SYSTEM_INCLUDE_PATH}")
message(STATUS "Set CMAKE_SYSTEM_LIBRARY_PATH to ${CMAKE_SYSTEM_LIBRARY_PATH}")

##########################################################################
# set compiler options for build types
##########################################################################
if(CMAKE_BUILD_TYPE MATCHES Release)
   set(CMAKE_C_FLAGS_RELEASE "-Os")
   set(CMAKE_CXX_FLAGS_RELEASE "-Os")
endif(CMAKE_BUILD_TYPE MATCHES Release)

if(CMAKE_BUILD_TYPE MATCHES RelWithDebInfo)
   set(CMAKE_C_FLAGS_RELWITHDEBINFO "-Os -save-temps -g -gdwarf-3 -gstrict-dwarf")
   set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-Os -save-temps -g -gdwarf-3 -gstrict-dwarf")
endif(CMAKE_BUILD_TYPE MATCHES RelWithDebInfo)

if(CMAKE_BUILD_TYPE MATCHES Debug)
   set(CMAKE_C_FLAGS_DEBUG "-O0 -save-temps -g -gdwarf-3 -gstrict-dwarf")
   set(CMAKE_CXX_FLAGS_DEBUG "-O0 -save-temps -g -gdwarf-3 -gstrict-dwarf")
endif(CMAKE_BUILD_TYPE MATCHES Debug)

##########################################################################
# compiler options for all build types
##########################################################################
add_definitions("-DF_CPU=${MCU_SPEED}")
add_definitions("-fpack-struct")
add_definitions("-fshort-enums")
add_definitions("-Wall")
add_definitions("-Werror")
add_definitions("-pedantic")
add_definitions("-pedantic-errors")
add_definitions("-funsigned-char")
add_definitions("-funsigned-bitfields")
add_definitions("-ffunction-sections")
add_definitions("-c")
add_definitions("-std=gnu99")

##########################################################################
# include search paths
##########################################################################

find_path(SIMAVR_INCLUDE_DIR
  NAMES "simavr/avr/avr_mcu_section.h"
  PATHS /usr/local/include/ /usr/include/
  NO_CMAKE_FIND_ROOT_PATH
  REQUIRED
)

include_directories(${SIMAVR_INCLUDE_DIR})

##########################################################################
# building library and application in their subdirectories
##########################################################################
add_subdirectory(Source)

##########################################################################
# testing functions w/o source files - gets FATAL_ERROR
##########################################################################
# add_avr_executable(test_breaks_generation)
# add_avr_library(mytestlib_breaks_generation)

##########################################################################
# custom commands
##########################################################################

add_custom_target(run
  COMMAND ${CMAKE_COMMAND} -E env ${CMAKE_SOURCE_DIR}/Meta/run.sh
  DEPENDS main
  USES_TERMINAL
)

add_custom_target(debug
  COMMAND ${CMAKE_COMMAND} -E env ${CMAKE_SOURCE_DIR}/Meta/debug.sh
  DEPENDS main
  USES_TERMINAL
)