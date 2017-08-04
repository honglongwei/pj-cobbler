auth  --useshadow  --enablemd5
bootloader --location=mbr
clearpart --all --initlabel
text
firewall --enabled
firstboot --disable
keyboard us
lang en_US
url --url=$tree
$yum_repo_stanza

network --onboot yes --device eth0 --bootproto=static --ip=192.168.222.222 --netmask=255.255.255.0 --gateway=192.168.222.1 
$SNIPPET('network_config')
clearpart --all --initlabel  
part /boot/efi --fstype=efi --size 200 
part /boot --fstype ext4 --size=200 --asprimary  
part / --fstype ext4 --size=15000 
part swap --size=1024
part /data --fstype ext4 --size=1 --grow 
reboot

rootpw --iscrypted $default_password_crypted
selinux --disabled
skipx
timezone   Asia/Shanghai
install
zerombr
user --name=root --password=richie 
%pre
$SNIPPET('log_ks_pre')
$SNIPPET('kickstart_start')
$SNIPPET('pre_install_network_config')
$SNIPPET('pre_anamon')
%end

%packages
@base  
@core 
@development
@server-platform-devel
lftp
samba-client
lftp
openssh-clients
epel-release 
%end

%post --nochroot
$SNIPPET('log_ks_post_nochroot')
%end

%post
$SNIPPET('log_ks_post')
chkconfig ip6tables off
cat >> /etc/security/limits.conf <<EOF
*           soft    nproc           65535
*           hard    nproc           65535
*           soft    nofile          102400
*           hard    nofile          204800
EOF
$yum_config_stanza
$SNIPPET('post_install_kernel_options')
$SNIPPET('post_install_network_config')
$SNIPPET('func_register_if_enabled')
$SNIPPET('download_config_files')
$SNIPPET('koan_environment')
$SNIPPET('redhat_register')
$SNIPPET('cobbler_register')
$SNIPPET('post_anamon')
$SNIPPET('kickstart_done')

%end
