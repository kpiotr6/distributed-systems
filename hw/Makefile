CC = gcc -g 
CCL = gcc -c -g -o 
BUILD = build
SRC = src

all:build_folder logger_b userstore_b server_b client_b

build_folder:
	mkdir -p ${BUILD}

server_b:	build_folder

	${CC} -o ${BUILD}/server ${SRC}/server.c ${BUILD}/libuserstore.a ${BUILD}/logger.a -pthread

client_b: 	build_folder

	${CC} -o ${BUILD}/client ${SRC}/client.c ${BUILD}/logger.a -pthread

userstore_b:	build_folder
	${CCL} ${BUILD}/userstore.o ${SRC}/userstore.c
	ar rcs ${BUILD}/libuserstore.a ${BUILD}/userstore.o
	rm ${BUILD}/userstore.o

logger_b:	build_folder
	${CCL} ${BUILD}/logger.o ${SRC}/logger.c
	ar rcs ${BUILD}/logger.a ${BUILD}/logger.o
	rm ${BUILD}/logger.o

clean:
	rm -r build

