python-tidb-replication
========================

[![Build Status](https://travis-ci.org/HashDataInc/pytidbrep.svg?branch=master)](https://travis-ci.org/HashDataInc/pytidbrep)

Pure Python Implementation of Tidb replication protocol. This allow you to receive event like insert, update, delete with their datas and raw SQL queries.

Use cases
===========

* Tidb to NoSQL database replication
* Tidb to search engine replication
* Invalidate cache when something change in database
* Audit
* Real time analytics

Documentation
==============

TODO

Installation
=============

```
pip install pytidbrep
```

Mailing List
==============

You can get support and discuss about new features on:
https://groups.google.com/forum/#!forum/tidb-user



Examples
=========


This example will dump all replication events to the console:

```python
from pytidbrep import BinLogStreamReader

stream = BinLogStreamReader('/path/to/binlog/dir')

for binlogevent in stream:
    print binlogevent

stream.close()
```

For this SQL sessions:

```sql
CREATE DATABASE test;
use test;
CREATE TABLE test4 (id int NOT NULL AUTO_INCREMENT, data VARCHAR(255), data2 VARCHAR(255), PRIMARY KEY(id));
INSERT INTO test4 (data,data2) VALUES ("Hello", "World");
UPDATE test4 SET data = "World", data2="Hello" WHERE id = 1;
DELETE FROM test4 WHERE id = 1;
```

Output will be:

```
391018326269895930: DDL: CREATE DATABASE test;
391018326269895973: DDL: use test; CREATE TABLE test4 (id int NOT NULL AUTO_INCREMENT, data VARCHAR(255), data2 VARCHAR(255), PRIMARY KEY(id));
391018326269896003: DML: INSERT test.test4: data "Hello", id 1, data2 "World", 
391018326269896009: DML: UPDATE test.test4: data "Hello" => "World", id 1 => 1, data2 "World" => "Hello", 
391018326269896018: DML: DELETE test.test4: data "World", id 1, data2 "Hello", 
```


Tests
========
use `tox` to run unit tests


Changelog
==========
[ChangeLog](https://github.com/HashDataInc/pytidbrep/blob/master/ChangeLog)


Contributors
==============

Major contributor:

* [Zhanwei Wang](https://github.com/wangzw)


Licence
=======
Copyright 2012-2017 HashData Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

