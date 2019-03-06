import argparse
import json
import sys
from pprint import pprint
import glob
import os
import MySQLdb

from mysqlparser import mysqlparser

G = '\033[92m'  # green
Y = '\033[93m'  # yellow
B = '\033[94m'  # blue
R = '\033[91m'  # red
W = '\033[0m'   # white

def readConfigFile(filePath):
    config = configparser.ConfigParser(allow_no_value = True)
    config.read(filePath)
    return config

def compareConfigValue(jsonValue, configValue):
    return jsonValue.strip() == configValue.strip()

def assessMySQLConfigFiles(directoryPath, verbose, configDataJsonPath, output):
    with open(configDataJsonPath, 'r') as file:
        jsonData = json.load(file)
    jsonData = jsonData['MySQLConfig']
    listConfigFiles = glob.glob(directoryPath + '/*.cnf')
    listConfigFiles.extend(glob.glob(directoryPath + '/*/*.cnf'))

    omitListFiles = ['debian.cnf']

    for filePath in listConfigFiles:

        isOmitFile = False
        for omitFile in omitListFiles:
            if omitFile in filePath:
                isOmitFile = True
        if isOmitFile:
            continue
        if verbose:
            print('\nOpen and working with file: ' + B + filePath + W)
        parser = mysqlparser.MySQLParser(filePath)
        results = parser.get()
        for result in results:
            header = result[0]
            body = result[1]
            if '!includedir' not in header:
                if verbose:
                    print('\n\tWorking with ' + B + '[' + header + ']' + W + ' field')
                for data in body:
                    key = str(data[0])
                    value = ''
                    if len(data) > 1:
                        value = str(data[1])
                    if verbose:
                        print('\t\tChecking field ' + G + '[' + key + '] : ' + Y + value + W)

                    if key in jsonData:
                        if not compareConfigValue(jsonData[key]['value'], value):
                            out = R + filePath +  ' [' + header + '][' + key + ']' + W + '\n'
                            out += B + 'Risk Scale: ' +  jsonData[key]['riskScale'] + W + '\n'
                            out += 'Expected Value: ' +  jsonData[key]['value'] + '\nYour value: ' + value + W + '\n'
                            out += Y + 'Description: ' +  jsonData[key]['description'] + W + '\n'
                            out += B + 'Url: ' + jsonData[key]['url'] + W + '\n\n'
                            print out
                            if output != None:
                                with open(output, 'a') as f:
                                    f.write(out.replace(R, '').replace(B, '').replace(Y, '').replace(G, '').replace(W, ''))
                    

def assessEachFeature(username, password, verbose, output):
    db = MySQLdb.connect(host='localhost', user=username, passwd=password)
    dbcurs = db.cursor()

    for file in os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/mysql'):
        if file.startswith('check_') and file.endswith('.py'):
            check = 'mysql.' + file[:-3]
            module = __import__(check)
            module = getattr(module, file[:-3])
            
            if verbose:
                print B + check + W
            module = module()
            
            dbcurs.execute(module.SQL)
            rows = dbcurs.fetchall()
            module.do_check(rows)

            result = module.result
            if 'level' in result:
                out = ''
                if result['level'].upper() == 'RED':
                    out = R + result['output'] + W
                elif result['level'].upper() == 'YELLOW':
                    out = Y + result['output'] + W
                elif result['level'].upper() == 'GREEN':
                    out = G + result['output'] + W
                print out
                if output != None and result['level'].upper() != 'GREEN':
                    with open(output, 'a') as f:
                        out = '\nPerforming check: ' + module.TITLE + '\nRisk level: ' + result['level'] + '\n' + out + '\n'
                        f.write(out.replace(R, '').replace(B, '').replace(Y, '').replace(G, '').replace(W, ''))


def assessMySQLDatabaseWithMySAT(username, password, outputHTML, verbose):
    if len(password) != 0:
        password = '-p' + password
    query = 'mysql --user={0} {1} --skip-column-names -f < ./MySAT/mysat.sql > {2}'.format(username, password, outputHTML)
    if verbose:
        print G + '\nChecking MySQL Database by using following command: ' + W
        print Y + query + W
    os.system(query)


def parser_error(errmsg):
    print("Usage: python " + sys.argv[0] + " [Options] use -h for help")
    print("Error: " + errmsg)
    sys.exit()


def parse_args():
    # parse the arguments
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0])
    parser.error = parser_error
    parser._optionals.title = "OPTIONS"
    parser.add_argument('-d', '--directory', help="Path to config file of MySQL", default='/etc/mysql')
    parser.add_argument('-u', '--username', help="MySQL username", default='root')
    parser.add_argument('-p', '--password', help="MySQL password", default='')
    parser.add_argument('-v', '--verbose', help='Enable Verbosity and display results in realtime', nargs='?', default=False)
    parser.add_argument('-o', '--output', help='Save the assess config files results to text file', default='outputConfigAssessment.txt')
    parser.add_argument('-ohtml', '--outputhtml', help='Save the asseess MySQL results to HTML file', default='outputMySQLSecurityAssessment.html')
    return parser.parse_args()

def main():
    args = parse_args()
    directoryPath = args.directory
    verbose = args.verbose
    if verbose or verbose is None:
        verbose = True
    output = args.output
    with open(output, 'w') as f:
        pass
    outputHTML = args.outputhtml
    configDataJsonPath = 'configData.json'
    username = args.username
    password = args.password

    assessMySQLConfigFiles(directoryPath, verbose, configDataJsonPath, output)
    assessEachFeature(username, password, verbose, output)
    assessMySQLDatabaseWithMySAT(username, password, outputHTML, verbose)

    
if __name__ == "__main__":
    main()