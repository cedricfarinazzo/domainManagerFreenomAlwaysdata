#!/usr/bin/python
# -*- coding: utf8 -*-

from conf import ALWAYSDATA_API_KEY, ALWAYSDATA_ACCOUNT, filename_domain
from tools import alwaysdata_init_auth, alwaysdata_clean_auth, \
        load_domains_from_file


def main():
    alwaysdata_init_auth(ALWAYSDATA_API_KEY, ALWAYSDATA_ACCOUNT)

    import freenom
    import alwaysdata

    print("Loading domains from file ...")
    domains = load_domains_from_file(filename_domain)
    print("domains list: %d domains" % (len(domains)))

    print("\n\n     HTTP CHECK  \n\n")
    freen = freenom.DomainCheckerFreenomDNS(domains)
    freen.check()
    to_do = {**freen.to_do}

    print("\n\n    ALWAYSDATA CHECK \n\n")
    alwaysd = alwaysdata.DomainCheckerAlwaysdata(domains, to_do)
    alwaysd.check()
    to_do = {**to_do, **alwaysd.to_do}

    print("\n\n    TO DO  \n\n")
    actionrequired = False
    for key, l in to_do.items():
        print("  * " + key)
        for e in l:
            print("- " + e.name + " | " + e.sitehost)
            actionrequired = True
        print()

    if actionrequired:
        confirm = ' '
        while confirm not in 'ynYN':
            confirm = input("confirm [y/n]: ")
        if confirm == 'y' or confirm == 'Y':
            alwaysd.update()
        else:
            print("abort")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise
    finally:
        alwaysdata_clean_auth()
