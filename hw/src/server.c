#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h>
#include <pthread.h>
#define _GNU_SOURCE 
#define __USE_GNU
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/un.h>
#include <math.h>
#include <signal.h>
#include <poll.h>
#include <pthread.h> 
#include <unistd.h>
#include "common.h"
#include "userstore.h"


AllClients userData = {.n = 0};
pthread_mutex_t userDataLock; 

SocketID createIPSocket(uint16_t port, Protocol protocol,char* serverIPAddress){
    SocketID fd = -1;
    struct sockaddr_in addr;
    int protocolCode;

    switch (protocol)
    {
        case TCP:
            protocolCode = SOCK_STREAM;
        break;
        case UDP:
            protocolCode = SOCK_DGRAM;
        break;
        default:
            return -1;
        break;
    }

    if ((fd = socket(AF_INET, protocolCode, 0)) == -1)
    {
        printf("a\n");
        return -1;
    }

    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_zero[0] = '\0';
    if (bind(fd,(const struct sockaddr *)&addr, sizeof(struct sockaddr_in)) ==-1)
    {
                printf("b\n");
        return -1;
    }
    if(protocol == TCP){
        if(listen(fd,MAX_WAITING)==-1){
            printf("c\n");
            return -1;
        }
    }

    return fd;
}
void* udpSocketThread(void* data){
    SocketID socket;
    ClassicMessage message;
    struct sockaddr_in addrSrc;
    socklen_t lenAddr = sizeof(struct sockaddr_in);
    socket = *((SocketID*)data);
    while(true){
        recvfrom(socket,&message,sizeof(ClassicMessage),0,&addrSrc,&lenAddr);
        if(strcmp(message.from,message.to)==0){
            pthread_mutex_lock(&userDataLock); 
            us_get_user(&userData,message.from)->udpAddr = addrSrc;
            pthread_mutex_unlock(&userDataLock); 

        }
        pthread_mutex_lock(&userDataLock); 
        addrSrc = us_get_user(&userData,message.to)->udpAddr;
        pthread_mutex_unlock(&userDataLock); 
        printf("UDP_READ\n");
        sendto(socket,&message,sizeof(ClassicMessage),0,&addrSrc,sizeof(struct sockaddr_in));
    }
}
void* socketThread(void* data){
    SocketID socket;
    struct sockaddr_in addr;
    ClassicMessage message;
    ControlMessage control;
    ClientData cd;

    socket = *((SocketID*)data);
    addr.sin_family = SOCK_DGRAM;

    read(socket,&control,sizeof(ControlMessage));

    memcpy(cd.name,control.name,strlen(control.name));
    cd.socketFd = socket;
    cd.udpAddr = control.in;
    
    pthread_mutex_lock(&userDataLock); 
    us_add_user(&userData,cd);
    pthread_mutex_unlock(&userDataLock); 

    write(socket,&control,sizeof(ControlMessage));

    printf("New thread started for user: %s\n",control.name);
    while(true){
        read(socket,&message,sizeof(ClassicMessage));
        if(message.end){
            write(socket,&message,sizeof(ClassicMessage));
            pthread_mutex_lock(&userDataLock); 
            us_remove_user(&userData,message.from);
            pthread_mutex_unlock(&userDataLock); 
            break;
        }
        else if(message.list){
            message.end = false;
            message.list = true;
            int currSize = 0;
            for(int i=0;i<userData.n;i++){
                snprintf(message.message+currSize,NAME_SIZE+1,"%s;",userData.data[i].name);
                currSize+=strlen(userData.data[i].name);
            }
            write(socket,&message,sizeof(ClassicMessage));
        }
        else{
            pthread_mutex_lock(&userDataLock); 
            cd = *us_get_user(&userData,message.to);
            pthread_mutex_unlock(&userDataLock); 

            write(cd.socketFd,&message,sizeof(ClassicMessage));
        }
    }
}

int main()
{
    SocketID tcpSocket;
    SocketID udpSocket;
    struct sockaddr_in addr;
    pthread_t thread_id;
    void* tData;
    int addrLen;
    int clientTCP;
    if (pthread_mutex_init(&userDataLock, NULL) != 0) { 
        perror("Unable to create mutex");
    } 
    if ((tcpSocket = createIPSocket(PORT,TCP,SERVER_IP)) == -1)
    {
        printf("%d\n",tcpSocket);
        perror("Unable to create TCP socket");
    }
    if ((udpSocket = createIPSocket(PORT,UDP,SERVER_IP)) == -1)
    {
        perror("Unable to create UDP socket");
    }
    tData = malloc(sizeof(SocketID));
    *((int*)tData) = udpSocket;
    pthread_create(&thread_id,NULL,udpSocketThread,tData);
    printf("Server ready\n");
    while(true){
        clientTCP = accept(tcpSocket,(const struct sockaddr * restrict )&addr,&addrLen);
        if(clientTCP == -1){
            // perror("Unable to accept connection");
        }
        else{

            tData = malloc(sizeof(SocketID));
            *((SocketID*)tData) = clientTCP;
            pthread_create(&thread_id,NULL,socketThread,tData);
        }
    }
    pthread_mutex_destroy(&userDataLock); 
    return 0;
}
