#include "userstore.h"
#include <string.h>


void us_add_user(AllClients* all, ClientData data){
  int i;
  for(i=0;i<all->n;i++);
  all->data[i] = data;
  all->n++;
}

ClientData* us_get_user(AllClients* all, char* name){
  for(int i=0;i<all->n;i++){
    if(strcmp(all->data[i].name,name)==0){
      return &(all->data[i]);
    }
  }
  return NULL;
}
void us_remove_user(AllClients* all, char* name){
  for(int i=0;i<all->n;i++){
    if(strcmp(all->data[i].name,name)==0){
      memmove(all->data+i,all->data+(i+1),(MAX_CLIENTS-i-1)*sizeof(ClientData));
      all->n--;
      break;
    }
  }
}
