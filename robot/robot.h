#pragma once

#include <assert.h>
#include <stdbool.h>

#define VERIFY(expr)    \
    do {                \
        sleep_cpu();    \
    } while (0)         \

#define ABORT() VERIFY(false);

#define VERIFY_NOT_REACHED() VERIFY(false)

int robot_init();
