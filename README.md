SchemaFS
========
SchemaFS allows you to use the filesystem as a database schema management interface.
Edit tables, triggers, views and stored procedures definitions the same way as you do it
while editing the application code - using your favorite text editor, file finder, IDE etc.

Just `sfs commit` your changes when you are done or use `sfs autocommit` feature to replicate it
to the database server in real time. And it's fully safe! Before each commit SchemaFS automatically checks
the server state for external changes and notifies you if your changes may conflict with others.

Example session
---------------
Suppose you have a project called "myproject" that uses `git` to version control and a simple PostgreSQL database to store the data.

    $ cd myproject
    $ tree -a
    .
    ├── .git
    ├── src
    └── some other existing project directories...

Let's see how we can start using SchemaFS to manage the database:

    $ sfs init --db mydb --use-existing --dir sql
    $ tree -a
    .
    ├── .git
    ├── src
    ├── some other existing project directories...
    ├── .schemafs
    │   ├── config
    │   └── some other metadata...
    └── sql
        └── mydb
            ├── functions
            │   └── some_function.sql
            │   └── some_other_function.sql
            └── tables
                └── some_table.sql

As you see SchemaFS just set up a directory structure that replicates your existing database schema.
Now, you can try to make some changes using any tools you like - `find` or Spotlight, `sed` or PyCharm etc...

    $ cat sql/mydb/functions/some_function.sql # just checking out some function definition
    CREATE OR REPLACE FUNCTION some_function(integer) RETURNS integer
    LANGUAGE sql AS $$
        SELECT value
        FROM some_table
        WHERE id = $1;
    $$;
    $ find . -type f -exec sed -i 's/value/volume/g' {} \; # performing a "rename" refactoring
    $ sfs diff # check out what we just made
    C some_table
    --- old
    +++ new
    @@ -1,5 +1,5 @@
     CREATE TABLE some_table (
         id integer NOT NULL,
    -    value integer,
    +    volume integer,
         data character varying
     );
    C some_function
    --- old
    +++ new
    @@ -3,6 +3,6 @@
     LANGUAGE sql AS $$
    -    SELECT value
    +    SELECT volume
         FROM some_table
         WHERE id = $1;
     $$;
    $ # as you see its just like `git diff`, but SchemaFS understands changes you made
    $ # and generates appropriate SQL queries to implement it on the DB side
    $ sfs diff --generated-sql
    BEGIN;
    -- C some_table
    ALTER TABLE some_table RENAME COLUMN value TO volume;
    -- C some_function
    CREATE OR REPLACE FUNCTION some_function(integer) RETURNS integer
    LANGUAGE sql AS $$
        SELECT volume
        FROM some_table
        WHERE id = $1;
    $$;
    COMMIT;
    $ sfs commit # execute generated SQL

How does SchemaFS know what I mean?
-----------------------------------
Suppose you have the `sfs diff` like this:

    C some_table
    --- old
    +++ new
    @@ -1,5 +1,5 @@
     CREATE TABLE some_table (
         id integer NOT NULL,
    -    value integer,
    +    volume integer,
         data character varying
     );

How SchemaFS can determine whether you wanted to rename the column or just drop it and create another?

SchemaFS uses an algorithm to calculate a list of ways to migrate from old database schema to the new one.
Most of the time this list contains only one possible way so SchemaFS can just generate SQL and execute it for you.
If it has several options for a particular situation it uses the non-destructive one by default, so you can revert
the changes later if you want. If there is no good guess SchemaFS allows you to choose action from the list or
execute a custom query.

Sounds great! Where you are now?
--------------------------------
For now SchemaFS can only replicate table and function definitions to the directory structure and make a simple diff.
But I am working on it. Watch the repository at https://github.com/vbo/schemafs to stay in touch.

I am targeting mostly PostgreSQL for now. MySQL and other databases support will be added after the first release.
