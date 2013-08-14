SQLFS
=====
SQLFS allows you to use the filesystem as a database administration interface.
Edit tables, triggers, views and stored procedures definitions the same way as you do it
while editing the application code - using your favorite text editor, file finder, IDE etc.

Just `sqlfs commit` your changes when you are done or use `sqlfs autocommit` feature to replicate it
to the database server in real time. And it's fully safe! Before each commit `sqlfs` automatically checks
the server state for external changes and notifies you if your changes may conflict with others.
