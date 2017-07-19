#include <stddef.h>
#include <unistd.h>

size_t fprint_string(int fd, const char *str);

size_t print_string(const char *str);

size_t read_string(char *str, size_t len);

size_t read_int();
