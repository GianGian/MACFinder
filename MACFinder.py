
from ciscoconfparse import CiscoConfParse
import os
import paramiko
from textwrap import wrap
import sys

def run_command_on_device(ip_address, username, password, command):
    """ Connect to a device, run a command, and return the output."""

    try:
         # Connect to router using username/password authentication.
        ssh.connect(ip, 
                        username=username1, 
                        password=password1,
                        look_for_keys=False)
            # Run command.
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
            # Read output from command.
        output = ssh_stdout.readlines()
        print("Attempt to connect...")
            # Close connection.
        ssh.close()
        return output

    except Exception as error_message:
        print("Unable to connect")
        sys.exit(error_message)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def print_topology (ipaddr,interface,name):
    width=19
    print('+-' + '-' * width + '-+')
    for line in wrap(name, width):
        print('| {0:^{1}} |'.format(line, width))
    for line in wrap(ipaddr, width):
        print('| {0:^{1}} |'.format(line, width))
    print('+-' + '-'*(width) + '-+')
    for line in wrap('|', width):
        print(' {0:^{1}} '.format(line, width))
    for line in wrap(interface, width):
        print(' {0:^{1}} '.format(line, width))
    for line in wrap('|', width):
        print(' {0:^{1}} '.format(line, width))

#get parameters
username1= input("Username: ")
password1=input("Password: ")
ip=input("Ip: ")
mac=input("Macaddress (XX:XX:XX:XX:XX:XX or XXXX.XXXX.XXXX): ")

#perform some check
try:
    response = os.system("ping " + ip)
    if response==0:
        print("Ping Successful, Host is UP!")
    else:
        raise Exception("Ping Unsuccessful, Host is DOWN.")
except Exception as error_message:
    sys.exit (error_message)

try:
    mac = mac.replace(":",'')
    mac = mac.replace(".",'')
    if len(mac)!=12:
        raise Exception ("MAC ERRATO")
    mac = '.'.join(mac[i:i+4] for i in range(0, len(mac), 4))
except Exception as error_message:
    sys.exit (error_message)

a=True
# inspect router
while(a==True):
    router_output = run_command_on_device(ip, username1, password1, "show mac address-table")
    name = router_output [0] #test
    r = [s for s in router_output if s.__contains__(mac)]
    if len(r)==0: sys.exit ('NO MAC')
    stringa = str(r[0])
    interface = stringa.split('    ')[3] #N=4 [N-1]

    #hostname
    hostname = run_command_on_device(ip, username1, password1, "show run | i hostname")
    hostname = str (hostname)
    name = hostname.split(' ')[1]
    name = name.split("\\")[0]

    #===
    if interface.__contains__("Po"):
        run = run_command_on_device(ip, username1, password1, "show run")

        parse = CiscoConfParse(run, syntax='ios')
        # Trova tutte le interfacce con un channel-group
        interfaces_with_channel_group = parse.find_objects_w_child(parentspec=r'^interface', childspec=r'channel-group')
        print (interfaces_with_channel_group)

    # Stampa le interfacce trovate
    for intf in interfaces_with_channel_group:
        interface = str(intf)
        interface = interface.split(' ')[4]
        interface = interface.removesuffix("'>")

        print (interface)
    #===
    print_topology(ip,interface,name)

    router_output2 = run_command_on_device(ip, username1, password1, "show cdp neighbors " + interface + " detail")
    #print (router_output2)
    if len(router_output2) != 0:
        t = [s for s in router_output2 if s.__contains__('IP address')]
        full_ip = str(t[0])
        ip = full_ip.split(':')[1]
        ip = ip.split("\\")[0]
    else:
        print("Arrivato all'oggetto")

        a=False
