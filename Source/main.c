#define __AVR_ATmega328P__
#include <avr/io.h>
#include <avr/sleep.h>

#include <stdio.h>
#include <simavr/avr/avr_mcu_section.h>
AVR_MCU(F_CPU, "atmega328");

#include "thingy.h"
#include "utilities.h"

enum PINS {
    PIN_POWER=PB0,
    PIN_USB,
    PIN_EN,
    PIN_SHUTDOWN,
    PIN_BOOT,
};

const struct avr_mmcu_vcd_trace_t _traces[] _MMCU_ = {
    { AVR_MCU_VCD_SYMBOL("PIN_SHUTDOWN"), .mask = (1 << PIN_SHUTDOWN), .what = (void*) &PORTB  }
};

int main(void)
{
    int ret = robot_init();
    if (ret < 0) {
        ABORT("robot_init failed");
    }

    DDRB = 1 << PIN_SHUTDOWN;
    PORTB |= 1 << PIN_SHUTDOWN;
    PORTB &= 0 << PIN_SHUTDOWN;
    PORTB |= 1 << PIN_SHUTDOWN;

    sleep_cpu();
    VERIFY_NOT_REACHED();
}
