#include "sandbox.h"

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>

void setup_sandbox()
{
#ifndef DEBUG
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0))
    {
        perror("prctl(NO_NEW_PRIVS)");
        exit(EXIT_FAILURE);
    }

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT))
    {
        perror("prctl(PR_SET_SECCOMP)");
        exit(EXIT_FAILURE);
    }
#endif
}   
