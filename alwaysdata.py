from alwaysdata_api import Auth, Domain, Site, Subdomain, SSLCertificate
from tools import isSubdomain
import checker


class DomainCheckerAlwaysdata(checker.DomainChecker):

    ALWAYSDATA_API_KEY = ""
    ALWAYSDATA_ACCOUNT_LIST = []
    account_data = {}

    def __init__(self, domains, to_do, ALWAYSDATA_API_KEY,
                 ALWAYSDATA_ACCOUNT_LIST):
        super().__init__(domains, to_do)
        self.ALWAYSDATA_API_KEY = ALWAYSDATA_API_KEY
        self.ALWAYSDATA_ACCOUNT_LIST = ALWAYSDATA_ACCOUNT_LIST
        self.account_data = {}
        for account in self.ALWAYSDATA_ACCOUNT_LIST:
            data = {"auth": Auth(account, self.ALWAYSDATA_API_KEY)}
            data["aldomains"] = Domain.list(auth=data["auth"])
            data["alsubdomains"] = Subdomain.list(auth=data["auth"])
            data["alsite"] = Site.list(auth=data["auth"])
            data["alsslcert"] = SSLCertificate.list(auth=data["auth"])
            self.account_data[account] = data

    def check(self):
        domains_add = []
        subdomains_add = []
        site_add_dom = []
        sslcert_add = []
        sslcert_assign = []
        sslcert_update = []

        for d in self.domains:
            if d.sitehost == 'extern':
                continue
            print("Check %s domain ..." % (d.name))
            if d.account is None:
                print(" ERROR account not specified")
                continue
            domain_account = self.account_data[d.account]
            aldomains = domain_account["aldomains"]
            alsubdomains = domain_account["alsubdomains"]
            alsite = domain_account["alsite"]
            alsslcert = domain_account["alsslcert"]

            found = False
            if not isSubdomain(d.name):
                for ad in aldomains:
                    if ad.name == d.name:
                        found = True
                        break
                if not found:
                    domains_add.append(d)
            else:
                for asd in alsubdomains:
                    if asd.hostname == d.name:
                        found = True
                        break
                if not found:
                    subdomains_add.append(d)

            found_site = False
            for asite in alsite:
                if asite.name == d.sitehost:
                    if d.name + '/' in asite.addresses:
                        found_site = True
                        break
            if not found_site:
                site_add_dom.append(d)

            ssl = None
            for assl in alsslcert:
                if d.name == assl.name:
                    ssl = assl
                    break
            if ssl is None:
                sslcert_add.append(d)
            else:
                alsubdom = None
                for e in alsubdomains:
                    if e.hostname == d.name:
                        alsubdom = e
                        break
                if alsubdom is None or alsubdom.ssl_certificate is None:
                    sslcert_add.append(d)
                elif alsubdom.ssl_certificate['href'] != ssl.href:
                    sslcert_assign.append(d)

        try:
            self.to_do["domains_add"] = self.to_do["domains_add"] + domains_add
        except Exception:
            self.to_do["domains_add"] = domains_add
        try:
            self.to_do["subdomains_add"] = self.to_do["subdomains_add"] \
                    + subdomains_add
        except Exception:
            self.to_do["subdomains_add"] = subdomains_add
        try:
            self.to_do["site_add_dom"] = self.to_do["site_add_dom"] \
                    + site_add_dom
        except Exception:
            self.to_do["site_add_dom"] = site_add_dom
        try:
            self.to_do["sslcert_add"] = self.to_do["sslcert_add"] + sslcert_add
        except Exception:
            self.to_do["sslcert_add"] = sslcert_add
        try:
            self.to_do["sslcert_assign"] = self.to_do["sslcert_assign"] \
                    + sslcert_assign
        except Exception:
            self.to_do["sslcert_assign"] = sslcert_assign
        try:
            self.to_do["sslcert_update"] = self.to_do["sslcert_update"] \
                    + sslcert_update
        except Exception:
            self.to_do["sslcert_update"] = sslcert_update

    def update(self):
        if self.to_do == []:
            self.check()
        for domain in self.to_do["domains_add"]:
            domain_account = self.account_data[domain.account]
            d = Domain(name=domain.name, auth=domain_account["auth"])
            try:
                d.post()
                print("Domain %s added to alwaysdatVya" % (domain.name))
            except Exception:
                print("Failed to add %s domain "
                      "to alwaysdata" % (domain.name))

        for domain in self.to_do["subdomains_add"]:
            if domain.sitehost == 'extern':
                continue
            domain_account = self.account_data[domain.account]
            site = None
            for e in self.alsite:
                if domain.name + '/' in e.addresses:
                    self.__remove_domain_site(domain, e)
            for e in self.alsite:
                if e.name == domain.sitehost:
                    site = e
                    break
            if domain.name + '/' in site.addresses:
                continue
            if site is None:
                print("Cannot find site "
                      "%s to add domain %s" % (domain.sitehost, domain.name))
                continue
            site.addresses.append(domain.name + '/')
            try:
                site.patch()
                print("SubDomain %s added "
                      "to %s site" % (domain.name, domain.sitehost))
            except Exception:
                print("Failed to add %s SubDomain "
                      "to %s site" % (domain.name, domain.sitehost))

        for domain in self.to_do["site_add_dom"]:
            if domain.sitehost == 'extern':
                continue
            site = None
            for e in self.alsite:
                if domain.name + '/' in e.addresses:
                    self.__remove_domain_site(domain, e)
            for e in self.alsite:
                if e.name == domain.sitehost:
                    site = e
                    break
            if site is None:
                print("Cannot find site %s to add "
                      "domain %s" % (domain.sitehost, domain.name))
                continue
            if domain.name + '/' in site.addresses:
                continue
            site.addresses.append(domain.name + '/')
            try:
                site.patch()
                print("Domain %s added to "
                      "%s site" % (domain.name, domain.sitehost))
            except Exception:
                print("Failed to add %s Domain to "
                      "%s site" % (domain.name, domain.sitehost))

        for domain in self.to_do["sslcert_add"]:
            domain_account = self.account_data[domain.account]
            ssl = SSLCertificate(name=domain.name, auth=domain_account["auth"])
            try:
                ssl.post()
                print("SslCertificate created for %s" % (domain.name))

            except Exception:
                print("Failed to create SslCertificate for %s."
                      " Try later. Maybe your certificate is "
                      "being created." % (domain.name))
            self.to_do["sslcert_assign"].append(domain)

        for domain in self.to_do["sslcert_assign"]:
            domain_account = self.account_data[domain.account]
            alsslcert = domain_account["alsslcert"]
            alsubdomains = domain_account["alsubdomains"]
            ssl = None
            for assl in alsslcert:
                if domain.name == assl.name:
                    ssl = assl
                    break
            alsubdom = None
            for e in alsubdomains:
                if e.hostname == domain.name:
                    alsubdom = e
                    break
            if ssl is None or alsubdom is None:
                print("Cannot found sslcertificate "
                      "or domain: %s" % (domain.name))
                continue
            alsubdom.ssl_certificate = ssl.id
            try:
                alsubdom.patch()
                print("Assign certificate to "
                      "%s domain" % (domain.name))
            except Exception:
                print("Failed to assign certificate to "
                      "%s domain" % (domain.name))

        for account_name, account_data in self.account_data.items():
            alsite = account_data["alsite"]
            for e in alsite:
                try:
                    e.restart()
                    print("Restart " + e.name)
                except Exception:
                    print("Failed to restart " + e.name)

    def __remove_domain_site(self, domain, site):
        site.addresses.remove(domain.name + '/')
        try:
            site.patch()
            print("Domain %s removed from %s site" % (domain.name, site.name))
        except Exception:
            print("Failed to remove %s "
                  "Domain from %s site" % (domain.name, domain.sitehost))
