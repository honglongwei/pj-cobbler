# pj-cobbler

```django
  python manage.py celery worker --loglevel=info
  /usr/local/bin/python manage.py runserver 8.8.8.8:8888 --insecure
```
```crb
cobbler import --path=/mnt --name=centos-6.9 arch=x86_64
cobbler profile edit --name="centos-6.9-x86_64"  --kickstart=/var/lib/cobbler/kickstarts/template_centos
```

### 网卡绑定
```cobbler
cobbler system edit --name=test-001 --interface=eth0 --mac=AA:BB:CC:DD:EE:00 --interface-type=bond_slave --interface-master=bond0 

cobbler system edit --name=test-001 --interface=eth1 --mac=AA:BB:CC:DD:EE:01 --interface-type=bond_slave --interface-master=bond0 

cobbler system edit --name=test-001 --interface=bond0 --interface-type=bond --bonding-opts="mode=active-backup miimon=100" --ip=192.168.3.167 --subnet=255.255.255.0 --gateway=192.168.3.1 --static=1

```
