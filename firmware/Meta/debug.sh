
TARGET="../build/Source/main-atmega328.elf"
echo "Debugging $TARGET"
simavr -m atmega328p -f 8000000 $TARGET -g &
avr-gdb
