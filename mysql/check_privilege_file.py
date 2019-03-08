class check_privilege_file():
    DESCRIPTION = """
    check_privilege_file:
    The following accounts have the FILE privilege. Do not grant to non Admin users.
    """
    REFERENCES = 'https://benchmarks.cisecurity.org/downloads/show-single/index.cfm?file=mysql.102'

    TITLE    = 'FILE Privilege'
    CATEGORY = 'Privilege'
    TYPE     = 'sql'
    SQL      = "SELECT user, host FROM mysql.user WHERE File_priv='Y'"

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
                output = 'No users found with FILE privilege.'

            self.result['output'] = output

        return self.result

    def __init__(self):
        print('Performing check: ' + self.TITLE)
