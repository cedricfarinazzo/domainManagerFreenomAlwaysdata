import sys
from pathlib import Path
import checker
import dns.resolver
sys.path.insert(0, str(Path(__file__).parent.joinpath("Freenom-dns-updater").resolve()))
import freenom_dns_updater
from datetime import date


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
                print("Alwaysdata nameservers not found in domain record!")
                dns_update.append(domain)
        try:
            self.to_do["dns_update"] = self.to_do["dns_update"] + dns_update
        except Exception:
            self.to_do["dns_update"] = dns_update


class DomainCheckerFreenomAPI(checker.DomainChecker):

    def __init__(self, *args, **kwargs):
        super(DomainCheckerFreenomAPI, self).__init__(*args, **kwargs)
        self.freenom = freenom_dns_updater.Freenom()

    def __domain_in_config(self, domainname):
        for d in self.domains:
            if d.name == domainname:
                return True
        return False

    def check(self, login, password):
        try:
            if not self.freenom.login(login, password):
                raise Exception()
            domains_list = self.freenom.list_domains()
        except Exception:
            print("Freenom API: Bad credentials. Cannot get domains list")
            return
        add_to_config = []
        need_renew = []
        for d in domains_list:
            print('Domain %s : ' % (d.name), end='  ')
            days_before_renew = (d.expire_date - date.today()).days
            ok = True
            if not self.__domain_in_config(d.name):
                add_to_config.append(d.name)
                print(' Not found in your config file', end=' ')
                ok = False
            if self.freenom.need_renew(d):
                need_renew.append(d.name)
                print(' Need renew :', days_before_renew,
                      "days", end=' ')
                ok = False
            if ok:
                print(' OK (', days_before_renew, 'days before renew)',
                      end='')
            print()
        try:
            self.to_do["add_to_config"] = self.to_do["add_to_config"] \
                    + add_to_config
        except Exception:
            self.to_do["add_to_config"] = add_to_config
        try:
            self.to_do["need_renew"] = self.to_do["need_renew"] \
                    + need_renew
        except Exception:
            self.to_do["need_renew"] = need_renew

    def update(self):
        try:
            domains_list = self.freenom.list_domains()
        except Exception:
            print("Freenom API: failed to get domain list")
            return
        for d in domains_list:
            if d.name in self.to_do["need_renew"]:
                try:
                    if not self.freenom.renew(d):
                        raise Exception()
                    print("Renew ", d.name)
                except Exception:
                    print("Failed to renew ", d.name)
