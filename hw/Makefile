CC = gcc -g 
CCL = gcc -c -g -o 
BUILD = build
SRC = src

all:build_folder  userstore_b server_b client_b

build_folder:
	mkdir -p ${BUILD}

server_b:	build_folder

	${CC} -o ${BUILD}/server ${SRC}/server.c ${BUILD}/libuserstore.a -pthread

client_b: 	build_folder

	${CC} -o ${BUILD}/client ${SRC}/client.c -pthread

userstore_b:	build_folder
	${CCL} ${BUILD}/userstore.o ${SRC}/userstore.c
	ar rcs ${BUILD}/libuserstore.a ${BUILD}/userstore.o
	rm ${BUILD}/userstore.o


