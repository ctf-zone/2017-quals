Organizers use this application for votes encryption. Each vote is a piece of data that looks like [‘ID’: x; ‘VOTE’: ‘ctfzone{xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}’], where ID – user identifier, VOTE – elector identifier.

We were informed that one user managed to vote for one candidate several times. Unfortunately, we cannot decrypt the votes and organizers refuse to assist. Please, help to understand who has this guy voted for.

The security of this cryptosystem is based on the difficulty of finding discrete logarithms modulo a large prime. The system parameters consist of a prime P and an integer G, whose powers modulo P generate a large number of elements, as in Diffie-Hellman. Application has next functions:

* Encrypt: encrypt(int(ptext, 16))
* Decrypt: format(decrypt(int(ctext)), "x")