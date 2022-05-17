SHELL := /bin/bash #to be able to execute bashcode
CCC = arm-angstrom-linux-gnueabi-gcc -march=armv7-a -mthumb -mfpu=neon -mfloat-abi=hard --sysroot=/usr/local/oecore-x86_64/sysroots/armv7at2hf-neon-angstrom-linux-gnueabi

server: server.c
	gcc -o server server.c

.ONESHELL:
SHELL := /bin/sh
cross:
	. /usr/local/oecore-x86_64/environment-setup-armv7at2hf-neon-angstrom-linux-gnueabi;
	$(CCC) -o lucky_server server.c

.PHONY:
clean: 
	rm -rf lucky_server server