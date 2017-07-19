#include <unistd.h>

typedef struct hashtable * hashtable_t;
typedef struct iterator * iterator_t;

hashtable_t hashtable_create(size_t capacity,
                             size_t (*hash)(const void *key),
                             int (*equals)(const void *key1, const void *key2),
                             void (*release)(void *key, void *data));

void hashtable_reset(hashtable_t hashtable);

void hashtable_free(hashtable_t hashtable);

void hashtable_insert(hashtable_t hashtable, void *key, void *data);

void *hashtable_get(hashtable_t hashtable, const void *key);

int hashtable_contains(hashtable_t hashtable, const void *key);

void hashtable_delete(hashtable_t hashtable, const void *key);

// hashtable callbacks for string keys
size_t string_hash(const void *key);

int string_equals(const void *key1, const void *key2);

// iterator
iterator_t iterator_create(hashtable_t table);

void iterator_delete(iterator_t iter);

void *iterator_next(iterator_t iter);
