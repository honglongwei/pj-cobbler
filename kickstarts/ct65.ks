auth  --useshadow  --enablemd5
unsupported_hardware
bootloader --location=mbr
clearpart --all --initlabel
$SNIPPET('diy/system_config_partition')
  
text
firewall --disable
firstboot --disable
keyboard us
lang en_US
url --url=$tree
$yum_repo_stanza
$SNIPPET('network_config')
reboot
 
rootpw --iscrypted $default_password_crypted
selinux --disabled
skipx
timezone Asia/Shanghai
install
zerombr
  
%packages
@base
@compat-libraries
@debugging
@development
%end

%pre
$SNIPPET('log_ks_pre')
$SNIPPET('kickstart_start')
$SNIPPET('pre_install_network_config')
$SNIPPET('pre_anamon')
%end
  
%post --nochroot
$SNIPPET('log_ks_post_nochroot')
%end

%post
$SNIPPET('log_ks_post')
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
