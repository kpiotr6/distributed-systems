#include "userstore.h"
#include <string.h>


void us_add_user(AllClients* all, ClientData data){
  int i;
  for(i=0;i<all->n;i++);
  all->data[i] = data;
  all->n++;
}

ClientData* us_get_user(AllClients* all, char* name){
  ClientData d = {.socketFd = -1};
  for(int i=0;i<all->n;i++){
    if(strcmp(all->data[i].name,name)==0){
      return &(all->data[i]);
    }
  }

  return &d;
}
void us_remove_user(AllClients* all, char* name){
  for(int i=0;i<all->n;i++){
    if(strcmp(all->data[i].name,name)==0){
      memcpy(all->data+i*sizeof(ClientData),all->data+(i+1)*sizeof(ClientData),(MAX_CLIENTS-i-1)*sizeof(ClientData));
      all->n--;
      break;
    }
  }
}
