#define __AVR_ATmega328P__
#include <avr/io.h>
#include <avr/sleep.h>
#include <stdio.h>
#include <util/delay.h>

#include "thingy.h"

int main(void)
{
    if (!robot_init()) {
        ABORT();
    }

    printf("hello test!\n");

    sleep_cpu();
    VERIFY_NOT_REACHED();
}
