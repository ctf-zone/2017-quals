#include "hashtable.h"

#include <stdlib.h>
#include <string.h>

struct bucket
{
    struct bucket *next;
    void *key;
    void *data;
};

struct hashtable
{
    size_t count;
    size_t nbuckets;
    struct bucket **buckets;
    size_t (*hash)(const void *key);
    int (*equals)(const void *key1, const void *key2);
    void (*release)(void *key, void *data);
};

struct iterator
{
    hashtable_t table;
    int cur_idx;
    struct bucket *cur_bucket;
};

hashtable_t hashtable_create(size_t capacity,
                             size_t (*hash)(const void *key),
                             int (*equals)(const void *key1, const void *key2),
                             void (*release)(void *key, void *data))
{
    hashtable_t hashtable = (hashtable_t)malloc(sizeof(struct hashtable));
    hashtable->count = 0;
    hashtable->nbuckets = capacity < 4 ? 4 : capacity;
    hashtable->buckets = (struct bucket **)calloc(capacity, sizeof(struct bucket *));
    hashtable->hash = hash;
    hashtable->equals = equals;
    
    return hashtable;
}

void hashtable_reset(hashtable_t hashtable)
{
    for (size_t i = 0; i < hashtable->nbuckets; i++)
    {
        struct bucket *b = hashtable->buckets[i];
        while (b != NULL)
        {
            b = b->next;
            hashtable->release(b->key, b->data);
            free(b);
        }
        hashtable->buckets[i] = NULL;
    }
}

void hashtable_free(hashtable_t hashtable)
{
    hashtable_reset(hashtable);
    free(hashtable->buckets);
    free(hashtable);
}

static void hashtable_grow(hashtable_t hashtable, size_t capacity)
{
    struct bucket **old = hashtable->buckets;
    struct bucket **new = (struct bucket **)calloc(capacity, sizeof(struct bucket *));
    
    for (size_t i = 0; i < hashtable->nbuckets; i++)
    {
        for (struct bucket *b = old[i]; b != NULL; b = b->next)
        {
            size_t new_idx = hashtable->hash(b->key) % capacity;
            b->next = new[new_idx];
            new[new_idx] = b;
        }
    }
    
    hashtable->nbuckets = capacity;
    hashtable->buckets = new;
}

void hashtable_insert(hashtable_t hashtable, void *key, void *data)
{
    size_t i = hashtable->hash(key) % hashtable->nbuckets;
    
    if (hashtable_contains(hashtable, key))
        return;
    
    struct bucket *b = (struct bucket *)malloc(sizeof(struct bucket));;
    b->next = hashtable->buckets[i];
    b->key = key;
    b->data = data;
    
    hashtable->buckets[i] = b;
    hashtable->count++;
    
    if (hashtable->count > hashtable->nbuckets)
        hashtable_grow(hashtable, hashtable->nbuckets * 2);
}

void *hashtable_get(hashtable_t hashtable, const void *key)
{
    size_t i = hashtable->hash(key) % hashtable->nbuckets;
    
    void *res = NULL;
    for (struct bucket *b = hashtable->buckets[i]; b != NULL; b = b->next)
    {
        if (hashtable->equals(b->key, key))
        {
            res = b->data;
            break;
        }
    }
    
    return res;
}

int hashtable_contains(hashtable_t hashtable, const void *key)
{
    return hashtable_get(hashtable, key) != NULL;
}

void hashtable_delete(hashtable_t hashtable, const void *key)
{
    size_t i = hashtable->hash(key) % hashtable->nbuckets;
    
    struct bucket *prev = NULL;
    for (struct bucket *b = hashtable->buckets[i]; b != NULL; prev = b, b = b->next)
    {
        if (hashtable->equals(b->key, key))
        {
            if (prev == NULL)
            {
                hashtable->buckets[i] = b->next;
            }
            else
            {
                prev->next = b->next;
            }
            
            free(b);
            break;
        }
    }
}

// hashtable callbacks
size_t string_hash(const void *key)
{
    const char *str = (const char *)key;
    size_t hash = 5381;
    int c;
    while ((c = *str++))
        hash = ((hash << 5) + hash) + c;

    return hash;
}

int string_equals(const void *key1, const void *key2)
{
    return strcmp((const char *)key1, (const char *)key2) == 0;
}

// iterator
iterator_t iterator_create(hashtable_t table)
{
    iterator_t iter = (iterator_t)malloc(sizeof(struct iterator));
    iter->table = table;
    iter->cur_idx = -1;
    iter->cur_bucket = NULL;
    return iter;
}

void iterator_delete(iterator_t iter)
{
    free(iter);
}

void *iterator_next(iterator_t iter)
{
    struct bucket *b = iter->cur_bucket;
    while (b == NULL)
    {
        iter->cur_idx += 1;
        if (iter->cur_idx == iter->table->nbuckets)
            return NULL;

        b = iter->table->buckets[iter->cur_idx];
    }

    iter->cur_bucket = b->next;

    return b->data;
}
