#include <stdbool.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include "logger.h"

void printError(char *message, bool useErrno, int line, char* file)
{
    if(useErrno){
        const char *errnoMesage = strerror(errno);
        fprintf(stderr, "%s %s %s %s %s %d %s\n", REDBG, "ERROR", RESET, message,errnoMesage,line,file);
    }
    else{
        fprintf(stderr, "%s %s %s %s %d %s\n", REDBG, "ERROR", RESET, message,line,file);
    }
	
}