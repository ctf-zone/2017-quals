#include "utils.h"
#include "heap.h"

#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <syscall.h>

#ifdef DEBUG
#include <stdio.h>
#endif

int send_string(int fd, const char *string)
{
    size_t len = string != NULL ? strlen(string) : 0;

#ifdef DEBUG
    printf("send_string: len: %lu\n", len);
    printf("send_string: buf: %s\n", string ? string : "");
#endif

    int res = write(fd, &len, sizeof(len));
    if (res != sizeof(len))
        return res;

    return write(fd, string, len);
}

static char *_recv_string(int fd, void *(*malloc_func)(size_t), void (*free_func)(void *))
{
    size_t len;
    int res = read(fd, &len, sizeof(len));
    if (res != sizeof(len))
        return NULL;

#ifdef DEBUG
    printf("recv_string: len: %lu\n", len);
#endif

    char *buf = malloc_func(len + 1);
    size_t i = 0;
    char *p = buf;
    while (i < len)
    {
        res = read(fd, &p[i], 1);
        if (res < 0)
        {
            free_func(buf);
            return NULL;
        }

        if (p[i] == '\0')
            break;

        i++;
    }

    buf[i] = '\0';

#ifdef DEBUG
    printf("recv_string: buf: %s\n", buf);
#endif

    return buf;
}

char *recv_string(int fd)
{
    return _recv_string(fd, malloc, free);
}

char *sec_recv_string(int fd)
{
    return _recv_string(fd, alloc, release);
}

void sec_exit(int ret)
{
    syscall(SYS_exit, ret);
}
