#include "io.h"

#include <stdlib.h>
#include <string.h>

size_t fprint_string(int fd, const char *str)
{
    if (str == NULL)
        return 0;

    size_t len = strlen(str);
    return write(fd, str, len);
}

size_t print_string(const char *str)
{
    return fprint_string(STDOUT_FILENO, str);
}

size_t read_string(char *str, size_t len)
{
    char chr;
    size_t cur_len = 0;

    while (cur_len < len)
    {
        int res = read(STDIN_FILENO, &chr, 1);
        if (res < 0)
            break;

        if (chr == '\n')
            break;
        
        str[cur_len] = chr;
        cur_len += res;
    }

    // One byte overflow here
    str[cur_len] = '\0';

    return cur_len;
}

size_t read_int()
{
    char str[32];
    read_string(str, sizeof(str));
    return strtoull(str, NULL, 10);
}
