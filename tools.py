import os

class PersonnalDomain:
    name = ""
    sitehost = ""

    def __init__(self, name, sitehost):
        self.name = name
        self.sitehost = sitehost

    def __str__(self):
        return "{%s; %s}" % (self.name, self.sitehost)

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        return self.name < other.name

def removeSpace(s):
    return ''.join(s.split(' '))

def load_domains_from_file(filename):
        domains = []
        with open(filename, 'r') as file:
            data = file.readlines()
        for i in data:
            if i.startswith('#') or i.strip() == '':
                continue
            j = i.strip().split(':')
            dom, host = removeSpace(j[0]), removeSpace(j[1])
            domains.append(PersonnalDomain(dom, host))
        domains.sort()
        return domains

def isSubdomain(url):
    return len(url.split('.')) == 3

def getDomainFromSubdomain(url):
    if not isSubdomain(url):
        return url
    return url.split('.')[1:]

def init_auth(api_key, account):
    os.environ['ALWAYSDATA_API_KEY'] = api_key
    os.environ['ALWAYSDATA_ACCOUNT']= account

def clean_auth():
    os.environ['ALWAYSDATA_API_KEY'] = ''
    os.environ['ALWAYSDATA_ACCOUNT']= ''
