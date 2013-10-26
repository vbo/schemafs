from subprocess import Popen, PIPE, STDOUT


def dump(server, user, db, args=None):
    if not args:
        args = []
        # todo: error handling
    if server != "localhost":
        cmd = 'ssh %s "pg_dump -s -U postgres %s -h localhost "' % (user + "@" + server, db)
    else:
        cmd = " ".join(
            ['pg_dump', '-s'] + args +
            ['-h', server, '-U', user, db]
        )
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True)
    sql = p.stdout
    return sql


