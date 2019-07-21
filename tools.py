class PersonnalDomain:
    name = ""
    account = None
    sitehost = ""

    def __init__(self, name, sitehost, account=None):
        self.name = name
        self.sitehost = sitehost
        self.account = account

    def __str__(self):
        if self.account is None:
            return "%s  |   %s" % (self.name, self.sitehost)
        return "%s  |   %s|%s" % (self.name, self.account, self.sitehost)

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
        host_conf = host.split('|')
        if len(host_conf) < 2:
            domains.append(PersonnalDomain(dom, host))
        else:
            domains.append(PersonnalDomain(dom, host_conf[1], host_conf[0]))
    domains.sort()
    return domains


def isSubdomain(url):
    return len(url.split('.')) == 3


def getDomainFromSubdomain(url):
    if not isSubdomain(url):
        return url
    return url.split('.')[1:]
