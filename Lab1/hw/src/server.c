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
#include "logger.h"

AllClients userData = {.n = 0};
pthread_mutex_t userDataLock;
SocketID tcpSocket;
SocketID udpSocket;


void closeServer()
{
    ClassicMessage message = INIT_CLASSIC_MESSAGE;
    message.end = true;
    for (int i = 0; i++; i < userData.n)
    {
        if (write(userData.data[i].socketFd, &message, sizeof(ClassicMessage)) == -1)
        {
            LOG_ERROR("Unable to send END message", true);
        }
        shutdown(userData.data[i].socketFd, SHUT_RDWR);
        close(userData.data[i].socketFd);
    }
    shutdown(tcpSocket, SHUT_RDWR);
    close(tcpSocket);
    close(udpSocket);
    exit(0);
}
void shutdownServer(int signo)
{
    printf("lol\n");
    closeServer();
}
SocketID createIPSocket(uint16_t port, Protocol protocol, char *serverIPAddress)
{
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
        LOG_ERROR("Unable to create socket", true);
        return -1;
    }

    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_zero[0] = '\0';
    if (bind(fd, (const struct sockaddr *)&addr, sizeof(struct sockaddr_in)) == -1)
    {
        LOG_ERROR("Unable bind socket", true);
        return -1;
    }
    if (protocol == TCP)
    {
        if (listen(fd, MAX_WAITING) == -1)
        {
            LOG_ERROR("Unable listen on socket", true);
            return -1;
        }
    }

    return fd;
}
void *udpSocketThread(void *data)
{
    SocketID socket;
    ClassicMessage message;
    struct sockaddr_in addrSrc;
    socklen_t lenAddr = sizeof(struct sockaddr_in);
    socket = *((SocketID *)data);
    free(data);
    while (true)
    {
        if (recvfrom(socket, &message, sizeof(ClassicMessage), 0, (struct sockaddr * restrict)&addrSrc, &lenAddr) == -1)
        {
            LOG_ERROR("Unable to read from UDP socket", true);
        }
        if (strcmp(message.from, message.to) == 0)
        {
            pthread_mutex_lock(&userDataLock);
            if (us_get_user(&userData, message.from) != NULL)
            {
                us_get_user(&userData, message.from)->udpAddr = addrSrc;
            }

            pthread_mutex_unlock(&userDataLock);
        }
        pthread_mutex_lock(&userDataLock);
        if (us_get_user(&userData, message.to) != NULL)
        {
            addrSrc = us_get_user(&userData, message.to)->udpAddr;
        }
        pthread_mutex_unlock(&userDataLock);
        if (sendto(socket, &message, sizeof(ClassicMessage), 0, (const struct sockaddr *)&addrSrc, sizeof(struct sockaddr_in)) == -1)
        {
            LOG_ERROR("Sending data through UDP socket failed", true);
        }
    }
}
void *socketThread(void *data)
{
    SocketID socket;
    ClassicMessage message;
    ControlMessage control;
    ClientData cd;

    socket = *((SocketID *)data);

    free(data);

    if (read(socket, &control, sizeof(ControlMessage)) == -1)
    {
        LOG_ERROR("Unable to read ControlMessage from TCP socket", true);
    }

    memcpy(cd.name, control.name, strlen(control.name));
    cd.socketFd = socket;
    cd.udpAddr = control.in;
    if (pthread_mutex_init(&(cd.tcpLock), NULL) != 0)
    {
        LOG_ERROR("Unable to create mutex", true);
    }
    pthread_mutex_lock(&userDataLock);
    us_add_user(&userData, cd);
    pthread_mutex_unlock(&userDataLock);

    if (write(socket, &control, sizeof(ControlMessage)) == -1)
    {
        LOG_ERROR("Unable to write ControlMessage to TCP socket", true);
    }

    printf("New thread started for user: %s\n", control.name);
    while (true)
    {
        if (read(socket, &message, sizeof(ClassicMessage)) == -1)
        {
            LOG_ERROR("Unable to read from TCP socket", true);
        }
        if (message.end)
        {
            if (write(socket, &message, sizeof(ClassicMessage)) == -1)
            {
                LOG_ERROR("Unable to write to TCP socket", true);
            }
            pthread_mutex_lock(&userDataLock);
            ClientData tmpData = *us_get_user(&userData, message.from);
            pthread_mutex_destroy(&(tmpData.tcpLock));
            shutdown(tmpData.socketFd, SHUT_RDWR);
            close(tmpData.socketFd);
            us_remove_user(&userData, message.from);
            pthread_mutex_unlock(&userDataLock);

            break;
        }
        else if (message.list)
        {
            message.end = false;
            message.list = true;
            int currSize = 0;
            pthread_mutex_lock(&userDataLock);
            for (int i = 0; i < userData.n; i++)
            {
                snprintf(message.message + currSize, NAME_SIZE + 1, "%s;", userData.data[i].name);
                currSize += strlen(userData.data[i].name);
            }
            pthread_mutex_unlock(&userDataLock);
            if (write(socket, &message, sizeof(ClassicMessage)) == -1)
            {
                LOG_ERROR("Unable to write to TCP socket", true);
            }
        }
        else
        {
            pthread_mutex_lock(&userDataLock);
            if (us_get_user(&userData, message.to) != NULL)
            {
                cd = *us_get_user(&userData, message.to);
                pthread_mutex_lock(&(cd.tcpLock));
                if (write(cd.socketFd, &message, sizeof(ClassicMessage)) == -1)
                {
                    LOG_ERROR("Unable to write to TCP socket", true);
                }
                pthread_mutex_unlock(&(cd.tcpLock));
            }
            pthread_mutex_unlock(&userDataLock);
        }
    }
}

int main()
{
    SocketID tcpSocket;
    SocketID udpSocket;
    struct sockaddr_in addr;
    pthread_t thread_id;
    void *tData;
    int addrLen;
    int clientTCP;

    signal(SIGINT, shutdownServer);

    if (pthread_mutex_init(&userDataLock, NULL) != 0)
    {
        LOG_ERROR("Unable to create mutex", true);
        exit(0);
    }
    if ((tcpSocket = createIPSocket(PORT, TCP, SERVER_IP)) == -1)
    {
        LOG_ERROR("Unable to create TCP socket", true);
        exit(0);
    }
    if ((udpSocket = createIPSocket(PORT, UDP, SERVER_IP)) == -1)
    {
        LOG_ERROR("Unable to create UDP socket", true);
        exit(0);
    }
    tData = malloc(sizeof(SocketID));
    *((int *)tData) = udpSocket;
    pthread_create(&thread_id, NULL, udpSocketThread, tData);
    printf("Server ready\n");
    while (true)
    {
        clientTCP = accept(tcpSocket, (struct sockaddr *restrict)&addr, &addrLen);
        if (clientTCP == -1)
        {
            LOG_ERROR("Unable to accept connection", true);
        }
        else
        {

            tData = malloc(sizeof(SocketID));
            *((SocketID *)tData) = clientTCP;
            pthread_create(&thread_id, NULL, socketThread, tData);
        }
    }
    pthread_mutex_destroy(&userDataLock);
    return 0;
}
