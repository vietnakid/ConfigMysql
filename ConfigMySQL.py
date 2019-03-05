import argparse
import json
import sys
from pprint import pprint
import glob

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

def workingWithMySQLConfigFiles(directoryPath, verbose, configDataJsonPath, output):
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
                                with open(output, 'wa') as f:
                                    f.write(out.replace(R, '').replace(B, '').replace(Y, '').replace(G, '').replace(W, ''))
                    
                


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
    parser.add_argument('-v', '--verbose', help='Enable Verbosity and display results in realtime', nargs='?', default=False)
    parser.add_argument('-o', '--output', help='Save the results to text file')
    return parser.parse_args()

def main():
    args = parse_args()
    directoryPath = args.directory
    verbose = args.verbose
    if verbose or verbose is None:
        verbose = True
    output = args.output
    configDataJsonPath = 'configData.json'
    workingWithMySQLConfigFiles(directoryPath, verbose, configDataJsonPath, output)

    
if __name__ == "__main__":
    main()