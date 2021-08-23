TARGET="../build/Source/main-atmega328.hex"
echo "Simulating $TARGET"
simavr -m atmega328p -f 8000000 $TARGET
