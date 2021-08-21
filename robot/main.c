#define __AVR_ATmega328P__
#include <avr/io.h>
#include <avr/sleep.h>
#include <util/delay.h>

int main(void)
{
    // make the LED pin an output for PORTB5
    DDRB = 1 << 5;

    while (1)
    {
        _delay_ms(500);

        // toggle the LED
        PORTB ^= 1 << 5;
    }

    sleep_cpu();

    return 0;
}
