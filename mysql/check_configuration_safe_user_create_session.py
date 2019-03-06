class check_configuration_safe_user_create_session():
    """
    check_configuration_safe_user_create_session:
    Prevent GRANT from creating a new user unless a non-empty also specified.
    """
    # References:
    # https://benchmarks.cisecurity.org/downloads/show-single/index.cfm?file=mysql.102

    TITLE    = 'Safe User Create (Session)'
    CATEGORY = 'Configuration'
    TYPE     = 'sql'
    SQL         = "SELECT @@session.sql_mode"

    verbose = False
    skip    = False
    result  = {}

    def do_check(self, *results):

        for rows in results:
            for row in rows:
                if 'NO_AUTO_CREATE_USER' == row[0]:
                    self.result['level']  = 'GREEN'
                    self.result['output'] = 'Safe user create is (%s) enabled.' % (row[0])
                else:
                    self.result['level']  = 'RED'
                    self.result['output'] = 'Safe user create is (%s) not enabled.' % (row[0])

        return self.result

    def __init__(self):
        print('Performing check: ' + self.TITLE)
