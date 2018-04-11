from vnxconfig import VNXConfig
import datetime
import time
from naviseccli import naviseccli

# Version 1.1 Alpha


def check_prereqs():
    cabspace_answer = input('Has reserve cab space been verified? (y or n): ').strip().lower()
    cabspace_verified = ''

    if cabspace_answer == 'y' or cabspace_answer == 'yes':
        cabspace_verified = True
    elif cabspace_answer == 'n' or cabspace_answer == 'no':
        cabspace_verified = False

def gather_array_info():
    print('Please answer the following questions to generate the naviseccli used to configure the array.')
    print()

    # Basic array information

    sp_a_ip = input('What is IP for SPA (10.x.x.x): ').strip().lower()
    sp_b_ip = input('What is IP for SPB (10.x.x.x): ').strip().lower()
    print()
    print('Running getagent on specified IPs, please wait...')
    print('----------------------------------------------------------------')
    getagent_a = naviseccli(host=sp_a_ip, user='sysadmin', passwd='sysadmin', command='getagent')
    getagent_b = naviseccli(host=sp_b_ip, user='sysadmin', passwd='sysadmin', command='getagent')
    print('SP A getagent:')
    for line in getagent_a:
        print(line)
    print()
    print('SP B getagent:')
    for line in getagent_b:
        print(line)
    print('----------------------------------------------------------------')
    print('Valid Datacenters:')
    print('DFW1, DFW3, ORD1, IAD2, IAD3, LON3, LON5, HKG1, SYD2, SYD4')
    print()

    dc_location = input('What DC is the array located in: ').strip().upper()

    account_num = input('What is the account number: ').strip().lower()

    device_num = input('What is the device number: ').strip().lower()

    # FastCache information collection

    fastcache_answer = input('Is the FastCache enabler installed and will it be used (y or n): ').strip().lower()
    fastcache_installed = ''

    if fastcache_answer == 'y' or fastcache_answer == 'yes':
        fastcache_installed = True
    elif fastcache_answer == 'n' or fastcache_answer == 'no':
        fastcache_installed = False

    fastcache_slots = []
    if fastcache_installed:
        fastcache_slot_answer = input('Are the FastCache drives installed at 0_0_4 and 0_0_5 (y or n): ').strip().lower()
        if fastcache_slot_answer == 'y' or fastcache_slot_answer == 'yes':
            fastcache_slots.append('0_0_4')
            fastcache_slots.append('0_0_5')
        else:
            for i in range(2):
                fastcache_slots.append(input('Enter FastCache drive {} location (ex. 0_0_4): '.format(i+1)).strip().lower())

    # Hotspare information collection
    hotspare_slots = []
    hotspare_answer = input('How many hotspares will be configured: ').strip().lower()
    if int(hotspare_answer) > 0:
        for i in range(int(hotspare_answer)):
            hotspare_slots.append(input('Hotspare {} (eg. 0_0_4 or 1_0_10): '.format(i + 1)))
    else:
        print("***WARNING: Please verify customer is aware of Rackspace minimum hotspare policy!***")

    print()

    storage_array = VNXConfig(sp_a_ip, sp_b_ip, dc_location, account_num, device_num, fastcache_installed, fastcache_slots, hotspare_slots)
    print('Warning! If you answer yes to the next question, management will be restarted on the SP IPs you specified.')
    automanage_answer = input('Would you like to disable automanage and restart CIMOM now? (y or n): ').strip().lower()

    if automanage_answer == 'y' or automanage_answer == 'yes':
        try:
            storage_array.disable_automanage()
            storage_array.restart_cimom()
        except Exception as err:
            print('Unexpected error: {}'.format(err))
            print('Please manually disable auto-manage...')

    return storage_array


def write_to_file(storage_array):
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H%M%S')
    filename = '{} {}.txt'.format(storage_array.array_info['Array Name'], timestamp)
    command_list = (storage_array.get_cli_commands())

    with open(filename, 'w') as file:
        file.write('naviseccli -addusersecurity -scope 0 -password sysadmin -user sysadmin')
        for command in command_list[:-2]:
            file.write('\nnaviseccli -h {} {}'.format(storage_array.array_info['SPA IP'], command))
        for command in command_list[-2:]:
            file.write('\nnaviseccli -h {} {}'.format(storage_array.array_info['SPB IP'], command))
        file.write('\n\n\n')
        file.writelines('%s\n' % l for l in storage_array.get_sp_aliases())
    print('Naviseccli command file created: {}'.format(filename))


if __name__ == "__main__":
    print('VNX Provisioning Assistant - 1.1 Alpha')
    print()
    print('This script is for EMC VNX 5100s only at this time')
    print('Please enter all answers carefully and verify your SP IPs before continuing. Use at your own risk!')
    print('Again, if you run this you are responsible for what happens. Not Rob, not Joe.')
    print('All commands are only GENERATED, not actually run. However, this script can disable automanage automatically.')
    print()
    proceed = input('Are you sure you want to continue? (y or n) ').strip().lower()
    if proceed == 'y' or proceed == 'yes':
        storage_array = gather_array_info()
        print()
        write_to_file(storage_array)
    elif proceed == 'n' or proceed == 'no':
        print('OK, Byeeeee!')
