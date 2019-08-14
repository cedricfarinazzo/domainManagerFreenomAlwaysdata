from alwaysdata_api import Auth, Domain, Site, Subdomain, SSLCertificate
from tools import isSubdomain
import checker


class DomainCheckerAlwaysdata(checker.DomainChecker):

    ALWAYSDATA_API_KEY = ""
    ALWAYSDATA_ACCOUNT_LIST = []
    ALWAYSDATA_ACCOUNT_DOMAIN = ""
    account_data = {}

    def __init__(self, domains, to_do, ALWAYSDATA_API_KEY,
                 ALWAYSDATA_ACCOUNT_LIST, ALWAYSDATA_ACCOUNT_DOMAIN):
        super().__init__(domains, to_do)
        self.ALWAYSDATA_API_KEY = ALWAYSDATA_API_KEY
        self.ALWAYSDATA_ACCOUNT_LIST = ALWAYSDATA_ACCOUNT_LIST
        self.ALWAYSDATA_ACCOUNT_DOMAIN = ALWAYSDATA_ACCOUNT_DOMAIN
        self.account_data = {}

        if self.ALWAYSDATA_ACCOUNT_DOMAIN not in self.ALWAYSDATA_ACCOUNT_LIST:
            raise Exception("ALWAYSDATA_ACCOUNT_DOMAIN must \
                    be in ALWAYSDATA_ACCOUNT_LIST")
        for account in self.ALWAYSDATA_ACCOUNT_LIST:
            data = {"auth": Auth(account, self.ALWAYSDATA_API_KEY)}
            data["aldomains"] = Domain.list(auth=data["auth"])
            data["alsubdomains"] = Subdomain.list(auth=data["auth"])
            data["alsite"] = Site.list(auth=data["auth"])
            data["alsslcert"] = SSLCertificate.list(auth=data["auth"])
            self.account_data[account] = data

    def check(self):
        account_domain = self.account_data[self.ALWAYSDATA_ACCOUNT_DOMAIN]
        domains_add = []
        subdomains_add = []
        site_add_dom = []
        sslcert_add = []
        sslcert_assign = []

        for d in self.domains:
            if d.sitehost == 'extern':
                continue
            print("Check %s domain ..." % (d.name))
            if d.account is None:
                print(" ERROR account not specified")
                continue
            domain_account = self.account_data[d.account]
            aldomains = account_domain["aldomains"]
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

            alsubdom = None
            for e in alsubdomains:
                if e.hostname == d.name:
                    alsubdom = e
                    break
            if alsubdom is not None and \
                    (alsubdom.ssl_certificate is None or
                     alsubdom.ssl_certificate['href'] != ssl.href):
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

    def update(self):
        if self.to_do == []:
            self.check()

        account_domain = self.account_data[self.ALWAYSDATA_ACCOUNT_DOMAIN]
        for domain in self.to_do["domains_add"]:
            for ac, ac_data in self.account_data.items():
                for d in ac_data["aldomains"]:
                    if d.name == domain.name:
                        self.__remove_domain(d, ac)
            d = Domain(name=domain.name)
            try:
                d.post(auth=account_domain["auth"])
                print("Domain %s added to alwaysdata" % (domain.name))
            except Exception:
                print("Failed to add %s domain "
                      "to alwaysdata" % (domain.name))

        for domain in self.to_do["subdomains_add"]:
            if domain.sitehost == 'extern':
                continue
            domain_account = self.account_data[domain.account]
            site = None
            for ac, ac_data in self.account_data.items():
                alsite = ac_data["alsite"]
                for e in alsite:
                    if domain.name + '/' in e.addresses:
                        self.__remove_domain_site(domain, e, ac)
            alsite = domain_account["alsite"]
            for e in alsite:
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
                site.patch(auth=domain_account["auth"])
                print("SubDomain %s added "
                      "to %s site" % (domain.name, domain.sitehost))
            except Exception:
                print("Failed to add %s SubDomain "
                      "to %s site" % (domain.name, domain.sitehost))

        for domain in self.to_do["site_add_dom"]:
            if domain.sitehost == 'extern':
                continue
            domain_account = self.account_data[domain.account]
            site = None
            for ac, ac_data in self.account_data.items():
                alsite = ac_data["alsite"]
                for e in alsite:
                    if domain.name + '/' in e.addresses:
                        self.__remove_domain_site(domain, e, ac)
            alsite = domain_account["alsite"]
            for e in alsite:
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
                site.patch(auth=domain_account["auth"])
                print("Domain %s added to "
                      "%s site" % (domain.name, domain.sitehost))
            except Exception:
                print("Failed to add %s Domain to "
                      "%s site" % (domain.name, domain.sitehost))

        for domain in self.to_do["sslcert_add"]:
            skip = False
            for ac, ac_data in self.account_data.items():
                for ssl in ac_data["alsslcert"]:
                    if ssl.name == domain.name:
                        if domain.account == ac:
                            skip = True
                            break
                        self.__remove_sslcert(ssl, ac)
                if skip:
                    break
            if skip:
                continue
            domain_account = self.account_data[domain.account]
            ssl = SSLCertificate(name=domain.name)
            try:
                ssl.post(auth=ac_data["auth"])
                self.to_do["sslcert_assign"].append(domain)
                print("SslCertificate created for %s" % (domain.name))
            except Exception:
                print("Failed to create SslCertificate for %s."
                      " Try later. Maybe your certificate is "
                      "being created." % (domain.name))

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
                alsubdom.patch(auth=domain_account["auth"])
                print("Assign certificate to "
                      "%s domain" % (domain.name))
            except Exception:
                print("Failed to assign certificate to "
                      "%s domain" % (domain.name))

        for account_name, account_data in self.account_data.items():
            alsite = account_data["alsite"]
            for e in alsite:
                try:
                    e.restart(auth=account_data['auth'])
                    print("Restart " + account_name + ":" + e.name)
                except Exception:
                    print("Failed to restart " + e.name)

    def __remove_domain_site(self, domain, site, account):
        site.addresses.remove(domain.name + '/')
        try:
            site.patch(auth=self.account_data[account]['auth'])
            print("Domain %s removed from %s site" % (domain.name, site.name))
        except Exception:
            print("Failed to remove %s "
                  "Domain from %s site" % (domain.name, domain.sitehost))

    def __remove_domain(self, domain, account):
        try:
            domain.delete(auth=self.account_data[account]['auth'])
            print("Domain %s removed" % (domain.name))
        except Exception:
            print("Failed to remove %s "
                  "Domain" % (domain.name))

    def __remove_sslcert(self, sslcert, account):
        try:
            sslcert.delete(auth=self.account_data[account]['auth'])
            print("SSL Certificate %s removed" % (sslcert.name))
        except Exception:
            print("Failed to remove %s "
                  "SSL Certificate" % (sslcert.name))
