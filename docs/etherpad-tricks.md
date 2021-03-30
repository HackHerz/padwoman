# Etherpad Tricks

## Improved database performance

Etherpad uses [ueberDB](https://github.com/ether/ueberDB) as its database driver, which transforms every Database into
a key-value-store. If you are using an MySQL-DB this will result in a lot of entries and therefore decreased performance.
A Better approach is to use a DB which already is a key-value store, like:

* [redis](https://redis.io)
* [ardb](https://github.com/yinqiwen/ardb)
* [rocksdb](https://github.com/facebook/rocksdb)
* [leveldb](https://github.com/google/leveldb)
* etc.
