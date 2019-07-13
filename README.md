## DomainManagerFreenomAlwaysdata

Manage your domains between Freenom and Alwaysdata


### Usage

- First install all dependencies : 
```
pip install -r requirements.txt
```

- Then copy conf.py.example to conf.py and edit it with your alwaysdata credentials

- Copy domain.txt.example and add all your freenom domain with the required syntax

- Then just run
```
python main.py
```

It will check if your domains are up.
Then it will check your alwaysdata configuration and it will propose you to do automatically something if need


### Help

#### How to add a freenom domain to alwaysdata ?

First go the the freenom dns management page of your domain and then go on Management Tools > Nameservers and set as following:
- Nameserver 1: dns1.alwaysdata.com
- Nameserver 2: dns2.alwaysdata.com
With this configuration, alwaysdata can manage your dns and you can do everything (domains, subdomains, email address, ...)


Then add a new line in the domain.txt file with the new domaine and the alwaysdata site for this domain.

Example:
```
example.com              :  mysite
```

Then run the python script


#### How to add a freenom subdomain to alwaysdata ?

Same as a domain. You just have to fill in name with the subdomain prefix.


#### How to change the alwaysdata site of a domain ?

Change it in the domain.txt file and run the python script!


## License

See the [LICENSE](./LICENSE) file for licensing information.

