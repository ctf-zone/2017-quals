#include "service.h"
#include "hashtable.h"
#include "candidate.h"
#include "utils.h"

#include <stdlib.h>

#ifdef DEBUG
#include <stdio.h>
#endif

static void service_check_candidate(hashtable_t table, int *pipefd)
{
    int read_fd = pipefd[0];
    int write_fd = pipefd[1];

    const char *citizen_id = recv_string(read_fd);
    if (citizen_id == NULL)
        return;

    int res = hashtable_contains(table, citizen_id);
    free((void *)citizen_id);
    write(write_fd, &res, sizeof(res));
}

static void candidate_cleanup(struct candidate *c)
{
    free((void *)c->firstname);
    free((void *)c->lastname);
    free((void *)c->citizen_id);
    free((void *)c->address);
}

static void service_store_candidate(hashtable_t table, int *pipefd)
{
    int read_fd = pipefd[0];
    int write_fd = pipefd[1];

    char *firstname = recv_string(read_fd);
    if (firstname == NULL)
        return;

    char *lastname = recv_string(read_fd);
    if (lastname == NULL)
        return;

    char *citizen_id = recv_string(read_fd);
    if (citizen_id == NULL)
        return;

    char *address = recv_string(read_fd);
    if (address == NULL)
        return;

    if (!hashtable_contains(table, citizen_id))
    {
        struct candidate *c = (struct candidate*)malloc(sizeof(struct candidate));
        c->firstname = firstname;
        c->lastname = lastname;
        c->citizen_id = citizen_id;
        c->address = address;
        c->cleanup = candidate_cleanup;

        hashtable_insert(table, citizen_id, c);
    }

    int res = 0;
    write(write_fd, &res, sizeof(res));
}

static void service_delete_candidate(hashtable_t table, int *pipefd)
{
    int read_fd = pipefd[0];
    int write_fd = pipefd[1];

    const char *citizen_id = recv_string(read_fd);
    if (citizen_id == NULL)
        return;

    hashtable_delete(table, citizen_id);
    free((void *)citizen_id);

    int res = 0;
    write(write_fd, &res, sizeof(res));
}

static void service_list_candidates(hashtable_t table, int *pipefd)
{
    int write_fd = pipefd[1];   

    iterator_t iter = iterator_create(table);
    void *p;
    int res;
    while ((p = iterator_next(iter)))
    {
        struct candidate *c = (struct candidate*)p;

#ifdef DEBUG
        printf("candidate: %p\n", c);
        printf("firstname: %s\n", c->firstname);
        printf("lastname: %s\n", c->lastname);
        printf("citizen_id: %s\n", c->citizen_id);
        printf("address: %s\n", c->address);
        printf("votes: %d\n", c->votes);
#endif

        res = 1;
        if (write(write_fd, &res, sizeof(res)) != sizeof(res))
            return;

        if (send_string(write_fd, c->firstname) < 0)
            return;

        if (send_string(write_fd, c->lastname) < 0)
            return;

        if (send_string(write_fd, c->citizen_id) < 0)
            return;

        if (send_string(write_fd, c->address) < 0)
            return;
            
        if (write(write_fd, &c->votes, sizeof(c->votes)) != sizeof(c->votes))
            return;

    }
    iterator_delete(iter);

    res = 0;
    write(write_fd, &res, sizeof(res));
}

static void service_vote_candidate(hashtable_t table, int *pipefd)
{
    int read_fd = pipefd[0];
    int write_fd = pipefd[1];

    const char *citizen_id = recv_string(read_fd);
    if (citizen_id == NULL)
        return;

    struct candidate *c = (struct candidate *)hashtable_get(table, citizen_id);
    if (c != NULL)
        c->votes += 1;

    free((void *)citizen_id);

    int res = (c == NULL) ? -1 : 0;
    write(write_fd, &res, sizeof(res));
}

void hashtable_release(void *key, void *data)
{
    struct candidate *c = (struct candidate *)data;
    if (key != c->citizen_id)
        free((void *)key);

    c->cleanup(c);
    free((void *)c);
}

void service_loop(int *pipefd)
{
    int read_fd = pipefd[0];

    hashtable_t table = hashtable_create(16,
                                         string_hash,
                                         string_equals,
                                         hashtable_release);

    while (1)
    {
        int opcode;
        int res = read(read_fd, &opcode, sizeof(opcode));
        if (res != sizeof(opcode))
            continue;

#ifdef DEBUG
        printf("got opcode: %d\n", opcode);
#endif

        switch (opcode)
        {
        case CHECK:
            service_check_candidate(table, pipefd);
            break;
        case STORE:
            service_store_candidate(table, pipefd);
            break;
        case DELETE:
            service_delete_candidate(table, pipefd);
            break;
        case LIST:
            service_list_candidates(table, pipefd);
            break;
        case VOTE:
            service_vote_candidate(table, pipefd);
            break;
        }
    }
}
