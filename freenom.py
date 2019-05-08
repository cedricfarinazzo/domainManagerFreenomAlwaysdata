import requests
import checker

class DomainCheckerFreenomDNS(checker.DomainChecker):

    def check(self):
        dns_update = []
        for domain in self.domains:
            print('Domain %s : ' % (domain.name), end='  ')
            try:
                r = requests.get('http://' + domain.name)
                print("%d OK" % (r.status_code)) 
            except:
                print("Failed to etablish a connection! FAILED")
                dns_update.append(domain)
        try:
            self.to_do["dns_update"] = self.to_do["dns_update"] + dns_update
        except:
            self.to_do["dns_update"] = dns_update

