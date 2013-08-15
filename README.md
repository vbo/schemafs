SchemaFS
========
SchemaFS allows you to use the filesystem as a database administration interface.
Edit tables, triggers, views and stored procedures definitions the same way as you do it
while editing the application code - using your favorite text editor, file finder, IDE etc.

Just `sfs commit` your changes when you are done or use `sfs autocommit` feature to replicate it
to the database server in real time. And it's fully safe! Before each commit `schemafs` automatically checks
the server state for external changes and notifies you if your changes may conflict with others.

Example session
---------------
Suppose you have a project called "myproject" that uses git to version control and a simple postgresql database to store the data.

    $ cd myproject
    $ tree -a
    .
    ├── .git
    ├── src
    └── some other existing project directories...

Let's see how we can start using `SchemaFS` to manage your database: 

    $ sfs init --db mydb --use-existing --dir sql
    $ tree -a
    .
    ├── .git
    ├── src
    ... some other existing project directories
    ├── .schemafs
    │   ├── config
    │   └── dumps
    │       └── working
    │           └── mydb.sql
    └── sql
        └── mydb
            ├── functions
            │   └── some_function.sql
            │   └── some_other_function.sql
            └── tables
                └── some_table.sql

As you see `SchemaFS` just set up a directory structure that replicates your existing database schema.
Now, you can try to make some changes using any tools you like - `find` or Spotlight, `sed` or PyCharm etc...

    $ cat sql/mydb/functions/some_function.sql # just checking out some function definition
    CREATE OR REPLACE FUNCTION some_function(integer) RETURNS integer
    LANGUAGE sql AS $$
        SELECT value
        FROM some_table
        WHERE id = $1;
    $$;
    $ find . -type f -exec sed -i 's/value/volume/g' {} \; # performing a "rename" refactoring
    $ sfs diff --generate-sql # check out diff in sql
    $ # todo: add sfs diff visuals
    $ sfs commit

TODO: tell something new ;)



