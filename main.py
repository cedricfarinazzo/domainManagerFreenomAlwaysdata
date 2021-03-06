#!/usr/bin/python
# -*- coding: utf8 -*-
import freenom
import alwaysdata

from conf import ALWAYSDATA_API_KEY, ALWAYSDATA_ACCOUNT_LIST, \
        FREENOM_EMAIL, FREENOM_PASSWORD, filename_domain, \
        ALWAYSDATA_ACCOUNT_DOMAIN
from tools import load_domains_from_file


def main():

    print("Loading domains from file ...")
    domains = load_domains_from_file(filename_domain)
    print("domains list: %d domains" % (len(domains)))

    to_do = {}
    print("\n\n     DNS CHECK  \n\n")
    freendns = freenom.DomainCheckerFreenomDNS(domains, to_do)
    freendns.check()
    to_do = freendns.to_do

    print("\n\n     FREENOM API CHECK  \n\n")
    freenapi = freenom.DomainCheckerFreenomAPI(domains, to_do)
    freenapi.check(FREENOM_EMAIL, FREENOM_PASSWORD)
    to_do = freenapi.to_do

    print("\n\n    ALWAYSDATA CHECK \n\n")
    alwaysd = alwaysdata.DomainCheckerAlwaysdata(domains, to_do,
                                                 ALWAYSDATA_API_KEY,
                                                 ALWAYSDATA_ACCOUNT_LIST,
                                                 ALWAYSDATA_ACCOUNT_DOMAIN)
    alwaysd.check()
    to_do = alwaysd.to_do

    print("\n\n    TO DO  \n\n")
    actionrequired = False
    for key, l in to_do.items():
        out_data = ""
        for e in l:
            out_data += "-  " + str(e) + "\n"
            actionrequired = True
        if len(l) > 0:
            print("  * " + key + "\n" + out_data + "\n")

    if actionrequired:
        confirm = ' '
        while confirm not in 'ynYN':
            confirm = input("confirm [y/n]: ")
        if confirm == 'y' or confirm == 'Y':
            print()
            freendns.update()
            print()
            freenapi.update(to_do=to_do)
            print()
            alwaysd.update()
            print()
        else:
            print("abort")
    else:
        print("Nothing...")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise
