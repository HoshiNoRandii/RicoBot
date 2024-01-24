### Configure the connection to the posgresql server
### using the database.ini file
from configparser import ConfigParser


# if listVals == True, values will be converted to lists
# they should be formatted in the original file like so:
######
## key=
##     value1
##     value2
##     value3
######
def config(filename="database.ini", section="postgresql", listVals=False):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)  # list of (name, value) pairs
        # make it a dict
        for param in params:
            if listVals:
                db[param[0]] = param[1].strip().splitlines()
            else:
                db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in the {filename} file")

    return db
