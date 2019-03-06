class check_configuration_local_infile():
    """
    check_configuration_local_infile:
    Local loading allows loading files from the client machine. This feature
    is sometimes used to perform data loading from remote machines.
    """
    # References:
    # https://dev.mysql.com/doc/refman/5.5/en/load-data-local.html
    # https://benchmarks.cisecurity.org/downloads/show-single/index.cfm?file=mysql.102

    TITLE    = 'Load Local data'
    CATEGORY = 'Configuration'
    TYPE     = 'sql'
    SQL         = "SHOW GLOBAL VARIABLES LIKE 'local_infile'"

    verbose = False
    skip    = False
    result  = {}

    def do_check(self, *results):

        for rows in results:
            for row in rows:
                if 'ON' == row[1]:
                    self.result['level']  = 'RED'
                    self.result['output'] = 'Load local data is (%s) enabled.' % (row[1])
                else:
                    self.result['level']  = 'GREEN'
                    self.result['output'] = 'Load local data is (%s) not enabled.' % (row[1])

            return self.result

    def __init__(self):
        print('Performing check: ' + self.TITLE)
