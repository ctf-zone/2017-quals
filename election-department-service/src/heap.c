#include "heap.h"
#include "io.h"
#include "utils.h"

#include <stdlib.h>
#include <stdio.h>
#include <sys/mman.h>
#include <sys/user.h>

struct chunk;
typedef struct chunk* chunkptr_t;

struct chunk
{
    size_t prev_size;
    size_t size;
    chunkptr_t fd;
    chunkptr_t bk;
};

#define HEAP_SIZE 0x1000000

#define ALIGNMENT          (2 * sizeof(size_t))
#define ALIGN_MASK         (ALIGNMENT - 1)

#define CHUNK_SIZE         (sizeof(struct chunk))
#define HEADER_SIZE        (2 * sizeof(size_t))

#define check_alignment(m) (((size_t)(m) & ALIGN_MASK) == 0)
#define align_size(m) \
    (((m) + HEADER_SIZE < CHUNK_SIZE) ? \
    sizeof(struct chunk) : \
    ((m) + HEADER_SIZE + ALIGN_MASK) & ~ALIGN_MASK)

#define PREV_INUSE 0x1
#define IS_LAST    0x2

#define SIZE_BITS (PREV_INUSE | IS_LAST)

#define chunk2mem(p)   ((void*)((char*)(p) + HEADER_SIZE))
#define mem2chunk(mem) ((chunkptr_t)((char*)(mem) - HEADER_SIZE))
#define chunksize(p)   ((p)->size & ~SIZE_BITS)
#define next_chunk(p)  ((chunkptr_t) (((char *)(p)) + chunksize(p)))
#define prev_chunk(p)  ((chunkptr_t) (((char *)(p)) - p->prev_size))

#define prev_inuse(p)       ((p)->size & PREV_INUSE)
#define set_prev_inuse(p)   (p)->size |= PREV_INUSE
#define clear_prev_inuse(p) (p)->size &= ~PREV_INUSE

#define inuse(p)       prev_inuse(next_chunk(p))
#define set_inuse(p)   set_prev_inuse(next_chunk(p))
#define clear_inuse(p) clear_prev_inuse(next_chunk(p))

#define islast_chunk(p)       ((p)->size & IS_LAST)
#define set_islast_chunk(p)   (p)->size |= IS_LAST
#define clear_islast_chunk(p) (p)->size &= ~IS_LAST

#define set_size(p, s) (p)->size = s | ((p)->size & SIZE_BITS)

static void *g_ptr;
static size_t g_size;

static chunkptr_t g_free_list;

__attribute__((constructor))
void init_heap()
{
    g_size = HEAP_SIZE;
    g_ptr = mmap(NULL, g_size + PAGE_SIZE, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (g_ptr == MAP_FAILED)
    {
        perror("mmap");
        sec_exit(EXIT_FAILURE);
    }

    g_free_list = (chunkptr_t)g_ptr;

    g_free_list->prev_size = 0;
    g_free_list->size = g_size;
    g_free_list->fd = NULL;
    g_free_list->bk = NULL;

    set_prev_inuse(g_free_list);
    set_islast_chunk(g_free_list);
    clear_inuse(g_free_list);
}

static void printerr(const char *str)
{
    fprint_string(STDERR_FILENO, str);
    abort();
}

static void unlink_chunk(chunkptr_t p)
{
    chunkptr_t next = p->fd;
    chunkptr_t prev = p->bk;

    if (prev == NULL)
    {
        g_free_list = next;
    }
    else
    {
        prev->fd = next;
    }

    if (next != NULL)
        next->bk = prev;
}

#ifdef DEBUG
void dump_chunk(chunkptr_t p)
{
    printf("p:            %p\n", p);
    printf("p->prev_size: %lu\n", p->prev_size);
    printf("p->size:      %lu\n", p->size);
    printf("p->fd:        %p\n", p->fd);
    printf("p->bk:        %p\n", p->bk);
}

void dump_heap()
{
    printf("free list:\n");
    chunkptr_t p;
    for (p = g_free_list; p != NULL; p = p->fd)
    {
        printf("--------------------------------\n");
        dump_chunk(p);
    }
    printf("--------------------------------\n");
}
#endif

void *alloc(size_t size)
{
#ifdef DEBUG
    printf("alloc(%lu)\n", size);
    dump_heap();
#endif
    size = align_size(size);

    chunkptr_t p;
    for (p = g_free_list; p != NULL; p = p->fd)
    {
        if (chunksize(p) >= size)
            break;
    }

    // out of memory
    if (p == NULL)
        return NULL;

    size_t rem_size = chunksize(p) - size;
    if (rem_size <= HEADER_SIZE)
    {
        set_inuse(p);
        unlink_chunk(p);
#ifdef DEBUG
        printf("alloc: chunk: %p mem: %p\n", p, chunk2mem(p));
        dump_heap();
#endif
        return chunk2mem(p);
    }

    chunkptr_t next = p->fd;
    chunkptr_t prev = p->bk;

    // split chunk
    chunkptr_t new_chunk = (chunkptr_t)((char*)p + size);
    new_chunk->fd = next;
    new_chunk->bk = prev;

    set_size(new_chunk, rem_size);
    set_prev_inuse(new_chunk);

    set_size(p, size);

    if (next != NULL)
    {
        next->bk = new_chunk;
    }
    else
    {
        set_islast_chunk(new_chunk);
        clear_islast_chunk(p);
    }
    
    if (prev != NULL)
    {
        prev->fd = new_chunk;
    }
    else
    {
        g_free_list = new_chunk;
    }
    
#ifdef DEBUG
    printf("alloc: chunk: %p mem: %p\n", p, chunk2mem(p));
    dump_heap();
#endif
    
    return chunk2mem(p);
}

void release(void *p)
{
#ifdef DEBUG
    printf("release(%p)\n", p);
    if (p != NULL)
    {
        printf("chunk:\n");
        dump_chunk(mem2chunk(p));
        dump_heap();
    }
#endif

    if (p == NULL)
        return;

    chunkptr_t chunk = mem2chunk(p);
    size_t size = chunksize(chunk);
    int is_last = islast_chunk(chunk);
    int is_consolidated = 0;

    chunkptr_t prev = prev_chunk(chunk);
    chunkptr_t next = NULL;

    if (!is_last)
        next = next_chunk(chunk);

    if (!check_alignment(size))
        printerr("release(): invalid size");

    // consolidate backward
    if (!prev_inuse(chunk))
    {
        size += chunksize(prev);
        unlink_chunk(prev);
        chunk = prev;
        is_consolidated = 1;
    }

    if (!is_last)
    {
        // consolidate forward
        if (!inuse(next))
        {
            size += chunksize(next);
            unlink_chunk(next);
            is_consolidated = 1;
        }
    }

    // add chunk to the head of free_list
    chunk->bk = NULL;
    chunk->fd = g_free_list;
    if (g_free_list != NULL)
        g_free_list->bk = chunk;
    g_free_list = chunk;

    set_size(chunk, size);

    next = next_chunk(chunk);
    if (is_consolidated || next->prev_size == 0)
        next->prev_size = size;
    clear_prev_inuse(next);

#ifdef DEBUG
    printf("release done\n");
    dump_heap();
#endif
}
