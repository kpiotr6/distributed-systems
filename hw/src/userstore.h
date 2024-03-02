#include "common.h"
#include <netinet/in.h> 



typedef struct ClientData {
  char name[NAME_SIZE];
  struct sockaddr_in  udpAddr;
  SocketID socketFd;
} ClientData;

typedef struct AllClients {
  ClientData data[MAX_CLIENTS];
  int n;
} AllClients;

void us_add_user(AllClients* all, ClientData data);
ClientData* us_get_user(AllClients* all, char* name);
void us_remove_user(AllClients* all, char* name);