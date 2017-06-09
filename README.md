Ssshare (Simple Secrets Sharing)
===

#### Secrets sharing system

Encrypts a secret, set up a quorum for the disclosure and give its pieces privately to shareholders.
At any point in the future, if enough participants agreed, the secret is rebuilt.

Ssshare is based on Dyne's FXC web-api & crypto-library, and it's able to make n-on-m secrets sharings.



##### Requirements
 - Python 3.4
 

##### Usage
```
$ setup.sh
$ . venv/bin/activate
$ ./run-ssshare
```

##### Tests
```
$ . venv/bin/activate
$ python -m unittest
```

##### How ?

Assuming the secret policy is a 2-on-3, the diagram is the following:

![Flow diagram](https://raw.githubusercontent.com/gdassori/ssshare/master/resources/secret_split_and_recovery.png)