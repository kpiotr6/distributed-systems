#define REDBG "\e[0;41m"
#define RESET "\e[0m"
#define LOG_ERROR(message, useErrno) printError(message,useErrno,__LINE__,__FILE__);

void printError(char *message, bool useErrno, int line, char* file);