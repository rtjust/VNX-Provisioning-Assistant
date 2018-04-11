import requests
from naviseccli import naviseccli
from lxml import html

requests.packages.urllib3.disable_warnings()


class VNXConfig():

    def __init__(self, sp_a_ip, sp_b_ip, dc_location, account_num, device_num, fastcache_installed, fastcache_slots, hotspare_slots):
        self.sp_a_ip = sp_a_ip
        self.sp_b_ip = sp_b_ip
        self.dc_location = dc_location
        self.account_num = account_num
        self.device_num = device_num
        self.fastcache_installed = fastcache_installed
        self.fastcache_slots = fastcache_slots
        self.hotspare_slots = hotspare_slots
        self.array_info = {}
        self.array_info['SPA IP'] = self.sp_a_ip
        self.array_info['SPB IP'] = self.sp_b_ip
        self.array_info['DC'] = self.dc_location
        self.array_info['Account Number'] = self.account_num
        self.array_info['Device Number'] = self.device_num
        self.array_info['FastCache'] = self.fastcache_installed
        self.array_info['FastCache slots'] = self.fastcache_slots
        self.array_info['Hotspare slots'] = self.hotspare_slots
        self.array_info['Array Name'] = '{}-{}-{}'.format(self.dc_location, self.account_num, self.device_num)
        self.array_info['SPA Name'] = '{}-{}-SPA'.format(self.dc_location, self.device_num)
        self.array_info['SPB Name'] = '{}-{}-SPB'.format(self.dc_location, self.device_num)
        self.array_info['SPA0 Alias'] = 'VNX_{}_{}_SPA0'.format(self.account_num, self.device_num)
        self.array_info['SPA1 Alias'] = 'VNX_{}_{}_SPA1'.format(self.account_num, self.device_num)
        self.array_info['SPA2 Alias'] = 'VNX_{}_{}_SPA2'.format(self.account_num, self.device_num)
        self.array_info['SPA3 Alias'] = 'VNX_{}_{}_SPA3'.format(self.account_num, self.device_num)
        self.array_info['SPB0 Alias'] = 'VNX_{}_{}_SPB0'.format(self.account_num, self.device_num)
        self.array_info['SPB1 Alias'] = 'VNX_{}_{}_SPB1'.format(self.account_num, self.device_num)
        self.array_info['SPB2 Alias'] = 'VNX_{}_{}_SPB2'.format(self.account_num, self.device_num)
        self.array_info['SPB3 Alias'] = 'VNX_{}_{}_SPB3'.format(self.account_num, self.device_num)
        self.array_info['Primary LDAP'] = self.get_dc_ldap(self.dc_location)[0]
        self.array_info['Secondary LDAP'] = self.get_dc_ldap(self.dc_location)[1]
        self.array_info['Primary NTP'] = self.get_dc_ntp(self.dc_location)[0]
        self.array_info['Secondary NTP'] = self.get_dc_ntp(self.dc_location)[1]
        self.array_info['DC Pass'] = self.get_dc_pass(self.dc_location)
        self.default_user = 'sysadmin'
        self.default_pass = 'sysadmin'


    def get_cli_commands(self):
        cli_list = []
        cli_list.append('getagent')
        cli_list.append('arrayname')
        cli_list.append('arrayname {} -o'.format(self.array_info['Array Name']))
        cli_list.append('arrayname')
        cli_list.append('spportspeed -set -sp A -portid 0 Auto -o')
        cli_list.append('spportspeed -set -sp A -portid 1 Auto -o')
        cli_list.append('spportspeed -set -sp A -portid 2 Auto -o')
        cli_list.append('spportspeed -set -sp A -portid 3 Auto -o')
        cli_list.append('spportspeed -set -sp B -portid 0 Auto -o')
        cli_list.append('spportspeed -set -sp B -portid 1 Auto -o')
        cli_list.append('spportspeed -set -sp B -portid 2 Auto -o')
        cli_list.append('spportspeed -set -sp B -portid 3 Auto -o')
        cli_list.append('port -list -sp -all')
        cli_list.append('faults -list')
        cli_list.append('environment -list -array -power')
        # TODO: VNX 5100 code below, add 5400 specific cache settings
        cli_list.append('setcache -wc 0 -rca 0 -rcb 0')
        cli_list.append('setcache -wsz 855 -p 8 -rsza 100 -rszb 100') # VNX 5100 Only
        cli_list.append('setcache -l 60 -h 80')
        cli_list.append('setcache -wc 1 -rca 1 -rcb 1')
        cli_list.append('getrg')
        cli_list.append('storagepool -list')
        cli_list.append('createrg 74 0_0_0 0_0_1 0_0_2 0_0_3')
        cli_list.append('bind r5 1017 -rg 74 -sq gb -cap 1')
        cli_list.append('chglun -l 1017 -name placeholder')
        cli_list.append('Security -list')
        cli_list.append('Security -adduser -user admin -password admin -scope global -role administrator -o')
        cli_list.append('Security -adduser -user san_scripts -password catRaXaP8U -scope global -role administrator -o')
        cli_list.append('Security -adduser -user emc -password admin -scope global -role operator -o')
        cli_list.append('Security -list')
        cli_list.append('storagegroup -enable')
        cli_list.append('ndu -list')
        if self.array_info['FastCache']:
            cli_list.append('cache -fast -create -disks {} {} -mode rw -rtype r_1'.format(self.array_info['FastCache slots'][0], self.array_info['FastCache slots'][1]))
        cli_list.append('setstats -on')
        cli_list.append('analyzer -get')
        cli_list.append('analyzer -set -narinterval 600')
        cli_list.append('analyzer -set -rtinterval 60')
        cli_list.append('analyzer -set -periodicarchiving 1')
        cli_list.append('analyzer -status')
        cli_list.append('analyzer -start')
        cli_list.append('analyzer -status')
        raidgroup = 74
        hotspare = 1017
        for slot in self.array_info['Hotspare slots']:
            raidgroup = raidgroup - 1
            hotspare = hotspare -1
            cli_list.append('createrg {} {}'.format(raidgroup, slot))
            cli_list.append('bind hs {} -rg {}'.format(hotspare, raidgroup))
        cli_list.append('Security -ldap -addserver {} -portnumber 389 -servertype AD -protocol LDAP -domainname storage.rackspace.com -binddn cn=storage,ou=ServiceAccounts,ou=Storage,ou=Rackspace,dc=storage,dc=rackspace,dc=com -bindpassword @p*mPnYT -usersearchpath ou=Rackspace,dc=storage,dc=rackspace,dc=com -groupsearchpath ou=Rackspace,dc=storage,dc=rackspace,dc=com'.format(
            self.array_info['Primary LDAP']))
        cli_list.append('Security -ldap -addrolemapping {} -name Architects-Storage -type group -role administrator -o'.format(self.array_info['Primary LDAP']))
        cli_list.append('Security -ldap -addrolemapping {} -name SAN-Engineers -type group -role administrator -o'.format(self.array_info['Primary LDAP']))
        cli_list.append('Security -ldap -addrolemapping {} -name Storage-Users -type group -role operator -o'.format(self.array_info['Primary LDAP']))
        cli_list.append('Security -ldap -addserver {} -o'.format(self.array_info['Secondary LDAP']))
        cli_list.append('Security -ldap -synchronize -o')
        cli_list.append('Security -ldap -listserver')
        cli_list.append('ntp -set -start yes -interval 10080 -servers {} {}'.format(self.array_info['Primary NTP'], self.array_info['Secondary NTP']))
        cli_list.append('Security -changeuserinfo -user admin -newpassword {} -scope global -o'.format(self.array_info['DC Pass']))
        cli_list.append('networkadmin -set -name {} -o'.format(self.array_info['SPA Name']))
        cli_list.append('networkadmin -get -name')
        cli_list.append('networkadmin -set -name {} -o'.format(self.array_info['SPB Name']))
        cli_list.append('networkadmin -get -name')

        return cli_list

    def get_sp_aliases(self):
        aliases = []
        aliases.append('### A Side ###')
        aliases.append(self.array_info['SPA1 Alias'])
        aliases.append(self.array_info['SPB0 Alias'])
       # aliases.append(self.array_info['SPA3 Alias'])
       # aliases.append(self.array_info['SPB2 Alias'])
        aliases.append('### B Side ###')
        aliases.append(self.array_info['SPA0 Alias'])
        aliases.append(self.array_info['SPB1 Alias'])
       # aliases.append(self.array_info['SPA2 Alias'])
       # aliases.append(self.array_info['SPB3 Alias'])

        return aliases

    def get_dc_ldap(self, datacenter):
        primary_ip = ''
        secondary_ip = ''
        if 'DFW' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        elif 'ORD' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        elif 'IAD' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        elif datacenter == 'LON3':
            primary_ip = ''
            secondary_ip = ''
        elif datacenter == 'LON5':
            primary_ip = ''
            secondary_ip = ''
        elif 'HKG' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        elif 'SYD' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        return primary_ip, secondary_ip

    def get_dc_ntp(self, datacenter):
        primary_ip = ''
        secondary_ip = ''
        if 'DFW' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        elif 'ORD' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        elif 'IAD' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        elif 'LON' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        elif 'HKG' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        elif 'SYD' in datacenter:
            primary_ip = ''
            secondary_ip = ''
        return primary_ip, secondary_ip

    def get_dc_pass(self, datacenter):
        password = ''
        if 'DFW' in datacenter:
            password = ''
        elif 'ORD' in datacenter:
            password = ''
        elif 'IAD' in datacenter:
            password = ''
        elif 'LON' in datacenter:
            password = ''
        elif 'HKG' in datacenter:
            password = ''
        elif 'SYD' in datacenter:
            password = ''
        return password

    def login_setup(self):
        spa_login = requests.post('https://{}/setup/login'.format(self.array_info['SPA IP']),
                                  data = {'Username': 'sysadmin', 'Password': 'sysadmin', 'method': 'navisphere',
                                          'Language': ''}, verify=False)
        spa_tree = html.fromstring(spa_login.content)
        spa_token = spa_tree.xpath('//input[@name="SecurityToken"]/@value')
        spb_login = requests.post('https://{}/setup/login'.format(self.array_info['SPB IP']),
                                  data = {'Username': 'sysadmin', 'Password': 'sysadmin', 'method': 'navisphere',
                                          'Language': ''}, verify=False)
        spb_tree = html.fromstring(spb_login.content)
        spb_token = spb_tree.xpath('//input[@name="SecurityToken"]/@value')
        return spa_token, spb_token

    def disable_automanage(self):
        print()
        print('Disabling automanage...')
        spa_token = self.login_setup()[0]
        spb_token = self.login_setup()[1]
        spa_disable_automanage = requests.post('https://{}/setup/setAutomanage'.format(self.array_info['SPA IP']),
                                               data={'AutoManage': 'Disable', 'SecurityToken': spa_token, 'Language': ''},
                                               verify=False)
        spb_disable_automanage = requests.post('https://{}/setup/setAutomanage'.format(self.array_info['SPB IP']),
                                               data = {'AutoManage': 'Disable', 'SecurityToken': spb_token, 'Language': ''},
                                               verify=False)

        if spa_disable_automanage.status_code == 200:
            print('SPA disabled')
        else:
            print('Failed to disable automanage on SPA')
        if spb_disable_automanage.status_code == 200:
            print('SPB disabled')
        else:
            print('Failed to disable automanage SPB')
        print()

    def restart_cimom(self):
        spa_token = self.login_setup()[0]
        spb_token = self.login_setup()[1]
        print()
        print('Restarting CIMOM on SPA and SPB...')
        spa_restart_cimom = requests.post('https://{}/setup/restartCIMOM'.format(self.array_info['SPA IP']),
                                          data = {'restart': 'Yes', 'SecurityToken': spa_token, 'Language': ''},
                                          verify=False)
        spb_restart_cimom = requests.post('https://{}/setup/restartCIMOM'.format(self.array_info['SPB IP']),
                                          data = {'restart': 'Yes', 'SecurityToken': spb_token, 'Language': ''},
                                          verify=False)

        if spa_restart_cimom.status_code == 200:
            print('SPA CIMOM restarted')
        else:
            print('Failed to restart SPA CIMOM')
        if spb_restart_cimom.status_code == 200:
            print('SPB CIMOM restarted')
        else:
            print('Failed to restart SPB CIMOM')

    def run_navicli(self, command, storage_processor):
        navi_result = ''
        if storage_processor.lower() == 'a':
            navi_result = naviseccli(host=self.array_info['SPA IP'], user=self.default_user, passwd=self.default_pass,
                                     command=command)
        elif storage_processor.lower() == 'b':
            navi_result = naviseccli(host=self.array_info['SPB IP'], user=self.default_user, passwd=self.default_pass,
                                     command=command)
        else:
            navi_result = 'Invalid storage processor specified: '.join(storage_processor)
        return navi_result

    def get_agent(self, storage_processor):
        print(self.run_navicli('getagent', 'SPA'))
