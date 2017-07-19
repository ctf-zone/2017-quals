int send_string(int fd, const char *string);

char *recv_string(int fd);

char *sec_recv_string(int fd);

void sec_exit(int ret);