#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/un.h>
#include <math.h>
#define _GNU_SOURCE         
#include <signal.h>
#include <poll.h>
#include <pthread.h> 
#include "common.h"

char name[NAME_SIZE];
struct sockaddr_in addrMulticast;
int initiateConnection(SocketID socketTcp,SocketID socketUdp, char* name){
    struct sockaddr_in addrUdp; 
    ControlMessage message = {
        .hello = true,
    };
    ClassicMessage initUdpmessage;
    
    memcpy(&(message.name),name,sizeof(char)*NAME_SIZE);
    memcpy(&(initUdpmessage.from),name,sizeof(char)*NAME_SIZE);
    memcpy(&(initUdpmessage.to),name,sizeof(char)*NAME_SIZE);
    if(write(socketTcp,&message,sizeof(ControlMessage))==-1){
        printf("s\n");
        return -1;
    }
    if(read(socketTcp,&message,sizeof(ControlMessage))==-1){
        printf("g\n");
        return -1;
    }
    if(write(socketUdp,&initUdpmessage,sizeof(ClassicMessage))==-1){
        printf("o\n");
        return -1;
    }
    if(read(socketUdp,&initUdpmessage,sizeof(ClassicMessage))==-1){
        printf("g\n");
        return -1;
    }


    return 0;
}
int configMulticastIP(struct sockaddr_in* addr){
    addr->sin_family = SOCK_DGRAM;
    addr->sin_port = htons(PORT);
    addr->sin_addr.s_addr = inet_addr(MULTICAST_IP);
    addr->sin_zero[0] = '\0';
}

SocketID createIPSocket(uint16_t port, Protocol protocol,char* serverIPAddress){
    struct sockaddr_in addrSock;
    SocketID fd = -1;
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

    addrSock.sin_family = AF_INET;
    addrSock.sin_port = htons(port);
    addrSock.sin_addr.s_addr = inet_addr(serverIPAddress);
    addrSock.sin_zero[0] = '\0';
    if(protocol == UDP){
        int loop=1;
        struct in_addr localInt;
        localInt.s_addr = htonl(INADDR_ANY);
        struct ip_mreq multicastReq;
        multicastReq.imr_multiaddr = addrMulticast.sin_addr;
        multicastReq.imr_interface = localInt;
        if(setsockopt(fd,IPPROTO_IP,IP_MULTICAST_LOOP,&loop,sizeof(int))==-1){
            printf("b\n");
            return -1;
        }
        if (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &multicastReq, sizeof(struct ip_mreq))) {
            printf("c\n");
            return -1;
        }
    }
    if(connect(fd,(const struct sockaddr *)&addrSock, sizeof(struct sockaddr_in)) == -1){
        printf("d\n");
        return -1;
    }
    return fd;
}
int sendMulticast(SocketID serverSocketUDP,char* message){
    ClassicMessage packedMessage = INIT_CLASSIC_MESSAGE;
    memcpy(&(packedMessage.from),name,strlen(name));
    memcpy(&(packedMessage.to),MULTICAST_IP,strlen(MULTICAST_IP));
    memcpy(&(packedMessage.message),message,strlen(message));
    sendto(serverSocketUDP,&packedMessage,sizeof(ClassicMessage),0,(const struct sockaddr *)&addrMulticast,sizeof(struct sockaddr_in));
}
int sendStandard(SocketID serverSocket,char* message, char* to){
    ClassicMessage packedMessage = INIT_CLASSIC_MESSAGE;
    memcpy(&(packedMessage.from),name,strlen(name));
    memcpy(&(packedMessage.to),to,strlen(to));
    memcpy(&(packedMessage.message),message,strlen(message));
    write(serverSocket,&packedMessage,sizeof(ClassicMessage));
}
int requestList(SocketID tcpSocket){
    ClassicMessage packedMessage = {
        .list = true,
        .end = false
    };
    memcpy(&(packedMessage.from),name,strlen(name));
    write(tcpSocket,&packedMessage,sizeof(ClassicMessage));
}
int endConnection(SocketID tcpSocket,SocketID udpSocket){
    ClassicMessage packedMessage = {
        .end = true,
    };
    memcpy(&(packedMessage.from),name,strlen(name));
    write(tcpSocket,&packedMessage,sizeof(ClassicMessage));
    // shutdown(tcpSocket,SHUT_RDWR);
    // shutdown(udpSocket,SHUT_RDWR);
    // close(tcpSocket);
    // close(udpSocket);
}

void readMessage(char* buff, int maxSize){
    int currPos = 0;
    int readAl;
    char* tmpPos;
    int tmpSize;
    getline(&buff, &maxSize, stdin);
    // while(true){
    //     tmpPos = buff+currPos;
    //     tmpSize = maxSize-currPos;
    //     readAl = getline(&tmpPos, &tmpSize, stdin);
    //     if(readAl==-1){
    //         ungetc((int)'a',stdin);
    //         break;
    //     }
    //     tmpPos+=currPos;
    // }
}

int userLoop(SocketID tcpSocket, SocketID udpSocket){
    char* buffer = malloc(sizeof(char)*MESSAGE_SIZE);
    char* bufferTmp = malloc(sizeof(char)*MESSAGE_SIZE);
    char* nameGiven = malloc(sizeof(char)*MESSAGE_SIZE);
    int tmpSize = MESSAGE_SIZE;
    while(true){

        int len;
        int prev = 0;
        // getline(&bufferTmp,&tmpSize,stdin)
        int val = getline(&bufferTmp,&tmpSize,stdin);
        switch (bufferTmp[0])
        {
            case 'S':
                getline(&nameGiven,&tmpSize,stdin);
                readMessage(buffer,MESSAGE_SIZE);
                sendStandard(tcpSocket,buffer,nameGiven);
                printf("\nMessage sent\n");
            break;
            case 'U':
                getline(&nameGiven,&tmpSize,stdin);
                readMessage(buffer,MESSAGE_SIZE);
                sendStandard(udpSocket,buffer,nameGiven);
                printf("\nMessage sent\n");
            break;
            case 'M':
                readMessage(buffer,MESSAGE_SIZE);
                sendMulticast(udpSocket,buffer);
                printf("\nMessage sent\n");
            break;
            case 'L':
                requestList(tcpSocket);
            break;
            case 'E':
                endConnection(tcpSocket,udpSocket);
            break;
        }
    }


}
void* recieveThread(void* data){
    SocketID socketTCP;
    SocketID socketUDP;
    struct pollfd fds[2];
    ClassicMessage message;
    int pollVal;
    int i;
    printf("New thread started\n");
    socketTCP = ((int*)data)[0];
    socketUDP = ((int*)data)[1];

    fds[0].fd = socketTCP;
    fds[0].events = POLLIN;

    fds[1].fd = socketUDP;
    fds[1].events = POLLIN;
    free(data);
    while(true){
        pollVal = poll(fds,2,-1);
        if(pollVal<=0){
            perror("Error with poll");
        }
        for(i=0;i<2;i++){
            if(fds[i].revents == POLLIN){
                break;
            }
        }
        read(fds[i].fd,&message,sizeof(ClassicMessage));
        if(message.end){
            printf("Recieved END message from server. Shutting down client\n");
            exit(0);
        }
        if(message.list){
            printf("Other users:\n");
            char* names;
            names = strtok(message.message,";");
            while(true){
                printf("%s\n",names);
                names = strtok(NULL,";");
                if(names == NULL){
                    break;
                }
            }
        }
        else {
            printf("From: %s\n",message.from);
            printf("%s",message.message);
        }

    }
}

int main()
{   
    SocketID socketTCP;
    SocketID socketUDP;
    pthread_t thread_id;
    struct sockaddr_in addrUDP;
    void* tData;

    tData = malloc(sizeof(int)*2+sizeof(struct sockaddr_in));


    printf("Select username: ");
    fgets(name,NAME_SIZE,stdin);

    configMulticastIP(&addrMulticast);
    if((socketTCP = createIPSocket(PORT,TCP,SERVER_IP))==-1){
        perror("Unable to create TCP socket");
    }
    if((socketUDP = createIPSocket(PORT,UDP,SERVER_IP))==-1){
        perror("Unable to create UDP socket");
    }
    // addrStdUDP = addrUDP;
    if(initiateConnection(socketTCP,socketUDP,name)){
        perror("Unable log into server");
    }
    else{
        printf("Your username is: %s\n",name);
    }
    ((int*)tData)[0] = socketTCP;
    ((int*)tData)[1] = socketUDP;

    pthread_create(&thread_id,NULL,recieveThread,tData);
    userLoop(socketTCP,socketUDP);
    return 0;
}
