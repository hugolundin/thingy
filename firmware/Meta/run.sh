
TARGET="../build/Source/main-atmega328.elf"
echo "Simulating $TARGET"
simavr -m atmega328p -f 8000000 $TARGET -v
