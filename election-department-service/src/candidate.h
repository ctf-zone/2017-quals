struct candidate
{
    char *firstname;
    char *lastname;
    char *citizen_id;
    char *address;
    unsigned int votes;

    void (*cleanup)(struct candidate *candidate);
};
