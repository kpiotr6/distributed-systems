#define _GNU_SOURCE
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

#include <signal.h>
#include <poll.h>
#include <pthread.h>
#include <signal.h>
#include <unistd.h>
#include "common.h"
#include "logger.h"

char name[NAME_SIZE];
SocketID socketTCP;
SocketID socketUDP;
SocketID socketMultiSend;
SocketID socketMultiRecv;

int endConnection()
{
    ClassicMessage packedMessage = {
        .end = true,
    };
    memcpy(&(packedMessage.from), name, strlen(name));
    
    if(write(socketTCP, &packedMessage, sizeof(ClassicMessage))==-1){
        LOG_ERROR("Unable to send ending message",true);
    }
    exit(0);
}

void shutdownClient(int signo){
  endConnection();
}


int initiateConnection(SocketID socketTcp, SocketID socketUdp, char *name)
{
    struct sockaddr_in addrUdp;
    ControlMessage message = {
        .hello = true,
    };
    ClassicMessage initUdpmessage;

    memcpy(&(message.name), name, sizeof(char) * NAME_SIZE);

    memcpy(&(initUdpmessage.from), name, sizeof(char) * NAME_SIZE);
    memcpy(&(initUdpmessage.to), name, sizeof(char) * NAME_SIZE);

    if (write(socketTcp, &message, sizeof(ControlMessage)) == -1)
    {
        LOG_ERROR("Unable to initiate connection",true);
        return -1;
    }
    if (read(socketTcp, &message, sizeof(ControlMessage)) == -1)
    {
        LOG_ERROR("Unable to initiate connection",true);
        return -1;
    }
    if (write(socketUdp, &initUdpmessage, sizeof(ClassicMessage)) == -1)
    {
        LOG_ERROR("Unable to initiate connection",true);
        return -1;
    }
    if (read(socketUdp, &initUdpmessage, sizeof(ClassicMessage)) == -1)
    {
        LOG_ERROR("Unable to initiate connection",true);
        return -1;
    }

    return 0;
}
SocketID createMulticastSocket(uint16_t port, char *addresIPMulticast, bool sending)
{
    int fd;
    int multiple = 1;
    int loop = 1;
    struct sockaddr_in addrIn;
    if ((fd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        LOG_ERROR("Unable to create multicast socket",true);
        return -1;
    }

    if (sending == true)
    {
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = inet_addr(addresIPMulticast);
        addr.sin_port = htons(port);
        addr.sin_zero[0] = '\0';
        if (connect(fd, (const struct sockaddr *)&addr, sizeof(struct sockaddr_in)) == -1)
        {
            LOG_ERROR("Unable to connect",true);
            return -1;
        }
    }
    else
    {
        if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &multiple, sizeof(int)) < 0)
        {
            LOG_ERROR("Reusing addreses failed",true);
            return -1;
        }
        if (setsockopt(fd, IPPROTO_IP, IP_MULTICAST_LOOP, &loop, sizeof(int)) < 0)
        {
            LOG_ERROR("Unable to loop multicast address",true);
            return -1;
        }

        addrIn.sin_family = AF_INET;
        addrIn.sin_addr.s_addr = htonl(INADDR_ANY);
        addrIn.sin_port = htons(port);
        addrIn.sin_zero[0] = '\0';

        struct ip_mreq mreq;
        mreq.imr_multiaddr.s_addr = inet_addr(addresIPMulticast);
        mreq.imr_interface.s_addr = htonl(INADDR_ANY);

        if (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0)
        {
            LOG_ERROR("Unable to join multicast group",true);
            return -1;
        }
        if (bind(fd, (struct sockaddr *)&addrIn, sizeof(struct sockaddr_in)) < 0)
        {
            LOG_ERROR("Unable to bind multicast socket",true);
            return -1;
        }
    }
    return fd;
}

SocketID createIPSocket(uint16_t port, Protocol protocol, char *serverIPAddress)
{
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
        LOG_ERROR("Unable to create socket",true);
        return -1;
    }

    addrSock.sin_family = AF_INET;
    addrSock.sin_port = htons(port);
    addrSock.sin_addr.s_addr = inet_addr(serverIPAddress);
    addrSock.sin_zero[0] = '\0';
    if (connect(fd, (const struct sockaddr *)&addrSock, sizeof(struct sockaddr_in)) == -1)
    {
        LOG_ERROR("Unable to connect to socket",true);
        return -1;
    }
    return fd;
}
int sendMulticast(SocketID serverSocketUDP, char *message)
{
    ClassicMessage packedMessage = INIT_CLASSIC_MESSAGE;
    memcpy(&(packedMessage.from), name, strlen(name));
    memcpy(&(packedMessage.to), MULTICAST_IP, strlen(MULTICAST_IP));
    memcpy(&(packedMessage.message), message, strlen(message));
    if(write(serverSocketUDP, &packedMessage, sizeof(ClassicMessage))==-1){
        LOG_ERROR("Unable to send data through multicast socket",true);
    }
}
int sendStandard(SocketID serverSocket, char *message, char *to)
{
    ClassicMessage packedMessage = INIT_CLASSIC_MESSAGE;
    memcpy(&(packedMessage.from), name, strlen(name));
    memcpy(&(packedMessage.to), to, strlen(to));
    memcpy(&(packedMessage.message), message, strlen(message));
    if(write(serverSocket, &packedMessage, sizeof(ClassicMessage))==-1){
        LOG_ERROR("Unable to create socket",true);
    }
}
int requestList(SocketID tcpSocket)
{
    ClassicMessage packedMessage = {
        .list = true,
        .end = false
    };
    memcpy(&(packedMessage.from), name, strlen(name));
    if(write(tcpSocket, &packedMessage, sizeof(ClassicMessage))==-1){
        LOG_ERROR("Unable to request list of users",true);
    }
}




int userLoop(SocketID tcpSocket, SocketID udpSocket, SocketID multicastSocket)
{
    char *buffer = malloc(sizeof(char) * MESSAGE_SIZE);
    char *nameGiven = malloc(sizeof(char) * MESSAGE_SIZE);
    int tmpSize = MESSAGE_SIZE;
    while (true)
    {
        getline(&buffer, (size_t * restrict)&tmpSize, stdin);
        switch (buffer[0])
        {
            case 'S':
                getline(&nameGiven, (size_t * restrict)&tmpSize, stdin);
                getline(&buffer,(size_t * restrict) &tmpSize, stdin);
                sendStandard(tcpSocket, buffer, nameGiven);
                break;
            case 'U':
                getline(&nameGiven, (size_t * restrict)&tmpSize, stdin);
                getdelim(&buffer, (size_t * restrict)&tmpSize,';', stdin);
                sendStandard(udpSocket, buffer, nameGiven);
                break;
            case 'M':
                getdelim(&buffer, (size_t * restrict)&tmpSize,';', stdin);
                sendMulticast(multicastSocket, buffer);
                break;
            case 'L':
                requestList(tcpSocket);
                break;
            case 'E':
                endConnection();
                break;
        }
    }
}
void *recieveThread(void *data)
{
    SocketID socketTCP;
    SocketID socketUDP;
    SocketID socketMulticast;
    struct pollfd fds[3];
    ClassicMessage message;
    int pollVal;
    int i;
    socketTCP = ((int *)data)[0];
    socketUDP = ((int *)data)[1];
    socketMulticast = ((int *)data)[2];

    fds[0].fd = socketTCP;
    fds[0].events = POLLIN;

    fds[1].fd = socketUDP;
    fds[1].events = POLLIN;

    fds[2].fd = socketMulticast;
    fds[2].events = POLLIN;
    free(data);
    while (true)
    {
        pollVal = poll(fds, 3, -1);
        if (pollVal <= 0)
        {
            LOG_ERROR("Poll failed",true);
        }
        for (i = 0; i < 3; i++)
        {
            if (fds[i].revents == POLLIN)
            {
                break;
            }
        }
        if(read(fds[i].fd, &message, sizeof(ClassicMessage))<=0){
            // LOG_ERROR("Unable to read from socket",true);
            printf("Recieved END message from server. Shutting down client\n");
            shutdown(socketTCP,SHUT_RDWR);
            close(socketTCP);
            close(socketUDP);
            close(socketMultiSend);
            close(socketMultiRecv);
            exit(0);
        }
        if (message.end)
        {
            printf("Recieved END message from server. Shutting down client\n");
            shutdown(socketTCP,SHUT_RDWR);
            close(socketTCP);
            close(socketUDP);
            close(socketMultiSend);
            close(socketMultiRecv);
            exit(0);
        }
        if (message.list)
        {
            printf("Other users:\n");
            char *names;
            names = strtok(message.message, ";");
            while (true)
            {
                printf("%s\n", names);
                names = strtok(NULL, ";");
                if (names == NULL)
                {
                    break;
                }
            }
        }
        else if(strcmp(message.from,name)!=0)
        {
            printf("From: %s", message.from);
            printf("%s\n", message.message);
        }
    }
}

int main()
{

    pthread_t thread_id;
    struct sockaddr_in addrUDP;
    void *tData;

    tData = malloc(sizeof(int) * 2 + sizeof(struct sockaddr_in));

    signal(SIGINT,shutdownClient);

    printf("Select username: ");
    fgets(name, NAME_SIZE, stdin);

    if ((socketTCP = createIPSocket(PORT, TCP, SERVER_IP)) == -1)
    {
        LOG_ERROR("Unable to create TCP socket",true);
        exit(0);
    }
    if ((socketUDP = createIPSocket(PORT, UDP, SERVER_IP)) == -1)
    {
        LOG_ERROR("Unable to create UDP socket",true);
        exit(0);
    }
    if ((socketMultiSend = createMulticastSocket(PORT_MULTICAST, MULTICAST_IP,true)) == -1)
    {
        LOG_ERROR("Unable to create UDP multicast sending socket",true);
        exit(0);
    }
    if ((socketMultiRecv = createMulticastSocket(PORT_MULTICAST, MULTICAST_IP,false)) == -1)
    {
        LOG_ERROR("Unable to create UDP multicast receiving socket",true);
        exit(0);
    }

    if (initiateConnection(socketTCP, socketUDP, name))
    {
        LOG_ERROR("Unable to log into a server",true);
        exit(0);
    }
    else
    {
        printf("Your username is: %s\n", name);
    }
    ((int *)tData)[0] = socketTCP;
    ((int *)tData)[1] = socketUDP;
    ((int *)tData)[2] = socketMultiRecv;
    pthread_create(&thread_id, NULL, recieveThread, tData);
    userLoop(socketTCP, socketUDP, socketMultiSend);
    return 0;
}
