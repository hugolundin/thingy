# thingy

## Setup

```bash
$ brew install avr-gcc avr-gdb  simavr cmake ninja
$ mkdir Build
$ cd Build
$ cmake -GNinja ..
$ ninja
$ ninja run
```

## Simulation

https://github.com/larsks/pipower

## Patching avr-gdb with elf32 support

It should be possible :^)

https://github.com/osx-cross/homebrew-avr/issues/216
https://blog.oddbit.com/post/2019-01-22-debugging-attiny-code-pt-1/
