#pragma once

#include <assert.h>
#include <stdbool.h>

// TODO: Add support for format args on log strings, for example: ("%d", int).

#define LOG(message)                                                           \
    do {                                                                       \
        printf("[%s:%d:%s]: %s\n", __FILE__, __LINE__, __func__, message);     \
    } while (0)                                                                \

#define VERIFY(expr)    \
    do {                \
        sleep_cpu();    \
    } while (0)         \

#define ABORT(message)  \
    do {                \
        LOG(message);   \
        sleep_cpu();    \
    } while (0)

#define VERIFY_NOT_REACHED()   \
    LOG("VERIFY_NOT_REACHED"); \
    VERIFY(false)
