# PandoraBot

A compact remote tester prototype for embedded device development.

It handles user's request via a simple web UI, and then calling some tools directly via `stdin`. Eventually when the tools complete the tasks, it reads the log from the tools' `stdout` and show it to users. 

## Tested devices

- Widora Neo
    - SPI/serial device: built-in
    - OS: OpenWrt mainline / OpenWrt 15.05 with MTK mods
    - Extra DTS mods is necessary, check [here](https://github.com/huming2207/openwrt/commit/716b0a12dde64b12974fb6eb43e4b89672f69c22#diff-aa3c6c11ba9d748287aa21cb2d4b786f)

- x86 PC
    - SPI Device: FTDI FT2232
    - Serial device: WCH CH340G
    - OS: Linux Mint 18.3

## Credit

- D-Team technology, Shenzhen (where I'm doing an full-time internship lol)
- Original FlashROM project
- Google Chromium OS's FlashROM fork
- OpenOCD project
- ttyd project

# To-do

- Basic CI Test
    - GPIO handling (key press simulations, etc.)
- Espressif tools support (esptool + espotatool)