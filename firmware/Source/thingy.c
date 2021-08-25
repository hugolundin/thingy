#define __AVR_ATmega328P__
#include <avr/io.h>
#include <avr/sleep.h>
#include <stdio.h>

#include "thingy.h"

static int uart_putchar(char c, FILE *stream)
{
    loop_until_bit_is_set(UCSR0A, UDRE0);
    UDR0 = c;
    return 0;
}

static FILE m_stdout = FDEV_SETUP_STREAM(
    uart_putchar,
    NULL,
    _FDEV_SETUP_WRITE
);

int robot_init()
{
    stdout = &m_stdout;
    return 1;
}