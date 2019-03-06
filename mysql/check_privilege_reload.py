class check_privilege_reload():
    """
    check_privilege_reload:
    The following accounts have the RELOAD privilege. Do not grant to non Admin users.
    """
    # References:
    # https://benchmarks.cisecurity.org/downloads/show-single/index.cfm?file=mysql.102

    TITLE    = 'RELOAD Privilege'
    CATEGORY = 'Privilege'
    TYPE     = 'sql'
    SQL      = "SELECT user, host FROM mysql.user WHERE Reload_priv='Y'"

    verbose = False
    skip    = False
    result  = {}

    def do_check(self, *results):
        if not self.skip:
            output               = ''
            self.result['level'] = 'GREEN'

            for rows in results:
                for row in rows:
                    self.result['level'] = 'RED'
                    output += row[0] + '\t' + row[1] + '\n'

            if 'GREEN' == self.result['level']:
                output = 'No users found with RELOAD privilege.'

            self.result['output'] = output

        return self.result

    def __init__(self):
        print('Performing check: ' + self.TITLE)
