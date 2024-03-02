
#include <stdbool.h>
#include <netinet/in.h> 
#include <unistd.h>
#pragma once

#define NAME_SIZE 32
#define INIT_CLASSIC_MESSAGE  { .list = false, .end = false}

#define MESSAGE_SIZE 16384

#define SERVER_IP "127.0.0.1"
#define MULTICAST_IP "230.0.0.1"
#define PORT 13218
#define PORT_MULTICAST 13334
#define MAX_WAITING 8
#define MAX_CLIENTS 8

 #define min(a,b) \
   ({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a < _b ? _a : _b; })

typedef int SocketID;

typedef enum Protocol{
    TCP,
    UDP
} Protocol;


typedef struct ClassicMessage {
  char from[NAME_SIZE];
  char to[NAME_SIZE];
  char message[MESSAGE_SIZE];
  bool list;
  bool end;
  
} ClassicMessage;

typedef struct ControlMessage {
  char name[NAME_SIZE];
  bool hello;
  struct sockaddr_in in;
}ControlMessage;



