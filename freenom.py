import sys
from pathlib import Path
import checker
import dns.resolver
sys.path.insert(0, str(Path(__file__).parent.joinpath("Freenom-dns-updater").resolve()))
import freenom_dns_updater


class DomainCheckerFreenomDNS(checker.DomainChecker):

    def check(self):
        dns_update = []
        for domain in self.domains:
            print('Domain %s : ' % (domain.name), end='  ')
            try:
                anwser_dns = dns.resolver.query(domain.name, 'NS')
                ns = []
                ns_ok = False
                for e in anwser_dns:
                    ns.append(str(e))
                ns_ok = "dns1.alwaysdata.com." in ns and \
                        "dns2.alwaysdata.com." in ns
                if not ns_ok:
                    raise Exception
                print(" OK")
            except Exception:
                print("Alwaysdata nameserver not found in domain record!")
                dns_update.append(domain)
        try:
            self.to_do["dns_update"] = self.to_do["dns_update"] + dns_update
        except Exception:
            self.to_do["dns_update"] = dns_update


class DomainCheckerFreenomAPI(checker.DomainChecker):

    def check(self, login, password):
        freenom = freenom_dns_updater.Frenom()
        if freenom.login(login, password):
            not_register = []
            need_renew = []
            domains_list = freenom.list_domains()
            for d in domains_list:
                if d.name not in self.domains:
                    not_register.append(d.name)
                if freenom.need_renew(d):
                    need_renew.append(d.name)
            try:
                self.to_do["not_register"] = self.to_do["not_register"] \
                        + not_register
            except Exception:
                self.to_do["not_register"] = not_register
            try:
                self.to_do["need_renew"] = self.to_do["need_renew"] \
                        + need_renew
            except Exception:
                self.to_do["need_renew"] = need_renew
        else:
            print("Connection failed to the Freenom API")

    def update(self):
        pass
