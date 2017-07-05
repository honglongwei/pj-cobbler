#_*_ coding:utf-8 _*_

import urllib2
import sys
import cobbler
import xmlrpclib 
from celery import task
from .models import AutoMsg, InstallRetMsg, OsinfoMsg
import subprocess
import random
import time
from subprocess import Popen, PIPE


class CobblerAPI(object):
    def __init__(self, url, user, password):
        self.cobbler_user= user
        self.cobbler_pass = password
        self.cobbler_url = url
    
    def add_system(self, hostname, ip_add, mac_add, profile, gateway):
        '''
        Add Cobbler System Infomation
        '''
        ret = {
            "result": True,
            "comment": [],
        }
        
        remote = xmlrpclib.Server(self.cobbler_url) 
        token = remote.login(self.cobbler_user, self.cobbler_pass) 
        system_id = remote.new_system(token) 
        remote.modify_system(system_id, "name", hostname, token) 
        remote.modify_system(system_id, "hostname", hostname, token) 
        remote.modify_system(system_id, 'modify_interface', { 
            "macaddress-eth0" : mac_add, 
            "ipaddress-eth0" : ip_add, 
            "dnsname-eth0" : hostname, 
            "static-eth0" : "True", 
            "subnet-eth0" : "255.255.255.0", 
        }, token) 
        remote.modify_system(system_id,"gateway", gateway, token)
        remote.modify_system(system_id, "profile", profile, token) 
       # remote.modify_system(system_id, "power_type", "ipmitool", token) 
       # remote.modify_system(system_id, "power_address", ipmi_add, token) 
       # remote.modify_system(system_id, "power_user", ipmi_user, token) 
       # remote.modify_system(system_id, "power_pass", ipmi_pass, token) 
        remote.save_system(system_id, token) 
        try:
            remote.sync(token)
        except Exception as e:
            ret['result'] = False
            ret['comment'].append(str(e))
        return ret

    def del_system(self, name):
        '''
        Delete Cobbler System Infomation
        '''
        ret = {
            "result": True,
            "comment": [],
        }

        remote = xmlrpclib.Server(self.cobbler_url)
        token = remote.login(self.cobbler_user, self.cobbler_pass)
        remote.remove_system(name, token)
        try:
            remote.sync(token)
        except Exception as e:
            ret['result'] = False
            ret['comment'].append(str(e))
        return ret


def chk_status(IP):
    try:
        cmd = "nc -v -w 1 {ip} 22".format(ip=IP)
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = proc.communicate()
        return stdout
    except:
        return False


@task()
def AutoInstall(ID):
    cobbler = CobblerAPI('http://127.0.1/cobbler_api', 'cobbler', 'cobbler')
    dt = AutoMsg.objects.get(id=ID)
    rt = InstallRetMsg(did=int(ID), status=1) 
    rt.save()
    hip = str(dt.IP).replace('.', '_')
    Host = 'opms-auto-{0}-{1}'.format(str(dt.id), hip) 
    try:
        ret = cobbler.add_system(hostname=Host, 
                                 ip_add=str(dt.IP), 
                                 mac_add=str(dt.Mac), 
                                 gateway=str(dt.GateWay), 
                                 profile=str(dt.osinfo) 
           )
        cmd = 'ipmitool -I lanplus -H {0} -U {1} -P {2} chassis bootdev pxe'.format(str(dt.IPMI_IP), str(dt.IPMI_User), str(dt.IPMI_Pass)) 
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        ret = proc.stdout.read().strip('\n')
        mlj = 'ipmitool -I lanplus -H {0} -U {1} -P {2} chassis power reset'.format(str(dt.IPMI_IP), str(dt.IPMI_User), str(dt.IPMI_Pass)) 
        prot = subprocess.Popen(mlj, stdout=subprocess.PIPE, shell=True)
        yy  = InstallRetMsg.objects.get(id=ID)
        yy.msg = u""
        yy.save()
        dt.HostName = Host
        dt.save()
        
        time.sleep(180)
        count = 0
        run_forever = True
        while run_forever:
            ret = chk_status(str(dt.IP))
            count += 1
            if 'succeeded' in ret:
                tb = InstallRetMsg.objects.get(id=ID)
                tb.status = 2
                tb.msg = u""
                tb.save() 
                try:
                    ret = cobbler.del_system(name='{0}'.format(str(Host)))
                except:
                    pass
                break 
            elif count == 350:
                tb = InstallRetMsg.objects.get(id=ID)
                tb.status = 3
                tb.msg = u""
                tb.save() 
                try:
                    ret = cobbler.del_system(name='{0}'.format(str(Host)))
                except:
                    pass
                break
            time.sleep(5)
        print count

        return ret
    except:
        return 'invaild params!'


@task()
def ForceEndInstall(ID):
    dt = AutoMsg.objects.get(id=ID)
    try:
        rt = InstallRetMsg.objects.get(did=int(ID))
        rt.status = -1
        rt.msg = u""
        rt.save()
    except:
        pass
    cobbler = CobblerAPI('http://127.0.0.1/cobbler_api', 'cobbler', 'cobbler')
    try:
        ret = cobbler.del_system(name='{0}'.format(str(dt.HostName)))
        return ret
    except:
        return 'system is alread delete !!!'
