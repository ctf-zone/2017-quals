#include "io.h"
#include "heap.h"
#include "utils.h"
#include "service.h"
#include "candidate.h"
#include "sandbox.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <sys/wait.h>
#include <syscall.h>

static void print_welcome()
{
    print_string("**********************************************\n");
    print_string("* Welcome to the election department service *\n");
    print_string("**********************************************\n");
}

static void print_menu()
{
    print_string("Choose action:\n");
    print_string("[1] Add candidate\n");
    print_string("[2] Vote for candidate\n");
    print_string("[3] List candidates\n");
    print_string("[4] Exit\n");
    print_string("> ");
}

static void print_add_candidate_menu()
{
    print_string("Add candidate:\n");
    print_string("[1] Set firstname\n");
    print_string("[2] Set lastname\n");
    print_string("[3] Set citizen id\n");
    print_string("[4] Set address\n");
    print_string("[5] Preview\n");
    print_string("[6] create and exit\n");
    print_string("[7] exit\n");
    print_string("> ");
}

static char *read_field(const char *field_name)
{
    print_string("Enter ");
    print_string(field_name);
    print_string(" length: ");

    size_t size = read_int();
    if (size == 0)
    {
        print_string("Invalid length!\n");
        return NULL;
    }

    char *buf = (char *)alloc(size);
    if (buf != NULL)
    {
        print_string("Enter ");
        print_string(field_name);
        print_string(": ");
        read_string(buf, size);
    }

    return buf;
}

static void print_field(const char *field_name, const char *value)
{
    print_string(field_name);
    print_string(": ");
    print_string(value);
    print_string("\n"); 
}

static int save_candidate(struct candidate *candidate, int *pipefd)
{
#ifndef DEBUG
    if (candidate->firstname == NULL || candidate->lastname == NULL ||
        candidate->citizen_id == NULL || candidate->address == NULL)
    {
        print_string("Please fill candidate info\n");
        return 0;
    }
#endif
    
    int read_fd = pipefd[0];
    int write_fd = pipefd[1];

    int opcode = STORE;
    int res = write(write_fd, &opcode, sizeof(opcode));
    if (res != sizeof(opcode))
        return 0;

    if (send_string(write_fd, candidate->firstname) < 0)
        return 0;

    if (send_string(write_fd, candidate->lastname) < 0)
        return 0;

    if (send_string(write_fd, candidate->citizen_id) < 0)
        return 0;

    if (send_string(write_fd, candidate->address) < 0)
        return 0;

    int op_res;
    res = read(read_fd, &op_res, sizeof(op_res));
    if (res < 0 || op_res != 0)
        return 0;

    return 1;
}

static void preview_candidate(struct candidate *candidate)
{
    print_string("Preview:\n");
    print_field("firstname", candidate->firstname);
    print_field("lastname", candidate->lastname);
    print_field("citizen_id", candidate->citizen_id);
    print_field("address", candidate->address);
}

static void candidate_cleanup(struct candidate *candidate)
{
    release(candidate->firstname);
    release(candidate->lastname);
    release(candidate->citizen_id);
    release(candidate->address);
}

static void add_candidate(int *pipefd)
{
    struct candidate candidate;
    memset(&candidate, 0, sizeof(struct candidate));
    candidate.cleanup = candidate_cleanup;

    while (1)
    {
        print_add_candidate_menu();
        int opt = read_int();
    
        switch (opt)
        {
        case 1:
            release(candidate.firstname);
            candidate.firstname = read_field("firstname");
            break;
        case 2:
            release(candidate.lastname);
            candidate.lastname = read_field("lastname");
            break;
        case 3:
            release(candidate.citizen_id);
            candidate.citizen_id = read_field("citizen id");
            break;
        case 4:
            release(candidate.address);
            candidate.address = read_field("address");
            break;
        case 5:
            preview_candidate(&candidate);
            break;
        case 6:
            if (save_candidate(&candidate, pipefd))
            {
                print_string("Candidate was added\n");
            }
            else
            {
                print_string("Error while adding candidate\n");
            }

            candidate.cleanup(&candidate);
            return;
        case 7:
            return;
        default:
            print_string("Invalid action\n");
        }
    }
}

static void vote_for_candidate(int *pipefd)
{
    int read_fd = pipefd[0];
    int write_fd = pipefd[1];

    const char *citizen_id = read_field("citizen id");
    if (citizen_id == NULL)
        return;

    int opcode = VOTE;
    int res = write(write_fd, &opcode, sizeof(opcode));
    if (res != sizeof(opcode))
    {
        print_string("Error while voting\n");
        return;
    }

    if (send_string(write_fd, citizen_id) < 0)
        return;

    int op_res;
    res = read(read_fd, &op_res, sizeof(op_res));
    if (res < 0)
    {
        print_string("Error while voting\n");
    } else if (op_res != 0)
    {
        print_string("Unknown citizen_id\n");
    }
}

static void list_candidates(int *pipefd)
{
    int read_fd = pipefd[0];
    int write_fd = pipefd[1];

    int opcode = LIST;
    int res = write(write_fd, &opcode, sizeof(opcode));
    if (res != sizeof(opcode))
    {
        print_string("Error while listing\n");
        return;
    }

    static const char *fields[] = {
        "firstname",
        "lastname",
        "citizen_id",
        "address",
    };
    static const size_t fields_num = sizeof(fields) / sizeof(*fields);

    int flag;
    while (1)
    {
        res = read(read_fd, &flag, sizeof(flag));
        if (res != sizeof(flag))
        {
            print_string("Error while listing\n");
            return; 
        }

#ifdef DEBUG
        printf("flag: %d\n", flag);
#endif
        if (flag == 0)
            break;

        const char *buf;

        for (int i = 0; i < fields_num; i++)
        {
            buf = sec_recv_string(read_fd);
            if (buf == NULL)
            {
                print_string("Error while listing\n");
                return;
            }

            print_field(fields[i], buf);
            release((void *)buf);
        }
        
        unsigned int votes;
        res = read(read_fd, &votes, sizeof(votes));
        if (res != sizeof(votes))
        {
            print_string("Error while listing\n");
            return;
        }
        
        char tmp[32];
        sprintf(tmp, "%d", votes);
        print_field("votes", tmp);
        
        print_string("\n");
    }
}

static void main_loop(int *pipefd)
{
    while (1)
    {
        print_menu();
        int opt = read_int();

        switch (opt)
        {
        case 1:
            add_candidate(pipefd);
            break;
        case 2:
            vote_for_candidate(pipefd);
            break;
        case 3:
            list_candidates(pipefd);
            break;
        case 4:
            sec_exit(EXIT_SUCCESS);
        default:
            print_string("Invalid action\n");
        }
    }
}

static void chld_handler(int sig)
{
    int status = 0;
    wait(&status);

//#ifdef DEBUG
    printf("chld_handler: sig: %d status: %d\n", sig, status);
//#endif
    
    if (WIFEXITED(status))
    {
        exit(WEXITSTATUS(status));
    }
    else if (WIFSIGNALED(status))
    {    
        int signum = WTERMSIG(status);
        switch (signum)
        {
            case SIGILL:
            case SIGABRT:
            case SIGFPE:
            case SIGSEGV:
            case SIGTRAP:
            case SIGKILL:
            case SIGBUS:
                exit(EXIT_FAILURE);
        }
    }
}

int main(int argc, char **argv)
{
    int pipefd[2];
    int pipefd1[2];
    int pipefd2[2];
    if (pipe(pipefd1) == -1 || pipe(pipefd2) == -1)
    {
        perror("pipe");
        sec_exit(EXIT_FAILURE);
    }

    pid_t pid = fork();
    if (pid == -1)
    {
        perror("fork");
        sec_exit(EXIT_FAILURE);
    }

    // child process
    if (pid == 0)
    {
        close(pipefd1[1]);
        close(pipefd2[0]);
        
        pipefd[0] = pipefd1[0];
        pipefd[1] = pipefd2[1];
        
        setup_sandbox();
        print_welcome();
        main_loop(pipefd);
    }
    else // parent process
    {
        close(pipefd1[0]);
        close(pipefd2[1]);
        
        pipefd[0] = pipefd2[0];
        pipefd[1] = pipefd1[1];
        
        struct sigaction sa;
        sa.sa_handler = &chld_handler;
        sa.sa_flags = SA_NOCLDSTOP;
        sigemptyset(&sa.sa_mask);
        
        if (sigaction(SIGCHLD, &sa, NULL) == -1)
        {
            perror("sigaction(SIGCHLD)");
            exit(EXIT_FAILURE);
        }
        
        service_loop(pipefd);
    }

    return 0;
}
