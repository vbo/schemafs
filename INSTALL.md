SchemaFS installation procedure
===============================
SchemaFS is very early in development for now and installation procedure may require some tweaking.

Linux/Mac OS X
--------------
1. `git clone` or just download sources and put it under e.g. `~/opt/schemafs`.
2. Create alias for `sfs` command line script using `alias sfs=~/opt/schemafs/sfs`.
3. Try to execute `sfs`. You probably see something like "sfs: Permission Denied". In this case use `chmod +x` to make script executable.
4. After this `sfs` must respond with brief usage explanation and die.

Windows
-------
We don't support Windows for now. If you fill enthusiastic download sources, call `schemafs.cli` module
using your python interpreter and try to fix errors ;) See #16 for details.
