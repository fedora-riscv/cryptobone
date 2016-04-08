%global cryptobonedir %{_prefix}/lib/%{name}

Name:       cryptobone
Version:    1.0.1   
Release:    11%{?dist}
Summary:    Secure Communication Under Your Control      

Group:      Applications/Internet         
License:    BSD and MIT     
URL:        https://crypto-bone.com      
Source0:    https://crypto-bone.com/release/source/cryptobone-1.0.1.tar.gz       

#BuildArch:  x86_64
ExclusiveArch: x86_64

BuildRequires: libbsd-devel
BuildRequires: gcc
BuildRequires: desktop-file-utils
BuildRequires: systemd


Requires: systemd
Requires: bash    
Requires: ksh
Requires: python
Requires: tkinter
Requires: openssh-askpass
Requires: fetchmail
Requires: base64
Requires: MTA 
#Suggests: postfix
Requires: socat
Requires: cryptsetup
Requires: openssh
Requires: nmap

Conflicts: cryptobone-extern

Provides: bundled(libcl.so) = 3.4.3

%description
The Crypto Bone is a secure messaging system that makes sure a user's
email is always encrypted without burdening the user with the message
key management. Based on a GUI and a separate daemon, both ease-of-use
and security are assured by a novel approach to encryption key management.

While the message keys are secured by a daemon running on the Linux machine,
additional protection can be achieved by using an external device for storing
encryption keys. This external device can be another Linux computer dedicated
to this task or a Beagle Bone or a Raspberry Pi.  (https://crypto-bone.com)


%prep
%setup 


%build
%configure
make %{?_smp_mflags}


%install
%make_install
mkdir -p %{buildroot}%{_datadir}/icons/default
cp %{buildroot}%{cryptobonedir}/GUI/cryptobone.png %{buildroot}%{_datadir}/icons/default
desktop-file-install --dir %{buildroot}%{_datadir}/applications -m 644 %{buildroot}%{cryptobonedir}/GUI/cryptobone.desktop


%post
# this script is run after the packet's installation 
if [ $1 -eq 1 ] ; then
     # installation only, not running after update
     echo
fi
/bin/touch --no-create %{_datadir}/icons/default &>/dev/null || :


%preun
# this script is run before the package is removed
if [ $1 -eq 0 ] ; then
     # removal only, not running before update
     systemctl stop cryptoboned
     systemctl disable cryptoboned
     systemctl disable cryptobone-fetchmail.timer
     umount %{cryptobonedir}/keys 2> /dev/null
     rm -f /etc/sudoers.d/cbcontrol
     if [ -f %{cryptobonedir}/bootswitch ] ; then
          chattr -i %{cryptobonedir}/bootswitch
     fi
     rm -rf /dev/shm/RAM
     # delete all config files in main cryptobone directory
     rm -rf %{cryptobonedir}/keys/* 2> /dev/null
     rm -rf %{cryptobonedir}/cryptobone/* 2> /dev/null
     rm -f %{cryptobonedir}/database* 2> /dev/null
     rm -f %{cryptobonedir}/cbb.config 2> /dev/null
     rm -f %{cryptobonedir}/bootswitch 2> /dev/null
     rm -f %{cryptobonedir}/keys.tgz 2> /dev/null
     rm -f %{cryptobonedir}/masterkey 2> /dev/null
     rm -f %{cryptobonedir}/pinghost 2> /dev/null
fi

%postun
# this script is run after the package is removed
if [ $1 -eq 0 ] ; then
     # just in case!
     rm -rf %{cryptobonedir} 2> /dev/null > /dev/null
     /bin/touch --no-create %{_datadir}/icons/default &>/dev/null
     /usr/bin/gtk-update-icon-cache %{_datadir}/icons/default &>/dev/null  || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/default &>/dev/null || :


%files
%{_unitdir}/cryptoboned.service
%{_unitdir}/cryptobone-fetchmail.service
%{_unitdir}/cryptobone-fetchmail.timer
%{_bindir}/cryptobone

# The directory %{cryptobonedir} contains security-critical files that need to be
# protected from being accessed by non-root users. In addition to restricting the
# main cryptobone directory to root-access, certain files will also have 0700 mode
# to ensure that they are protected even if (accidentally) the directory permission
# might be changed. In particular, this is crucial for the keys subdirectory.
%{cryptobonedir}

%{_datadir}/applications/cryptobone.desktop
%{_datadir}/icons/default/cryptobone.png

%{_mandir}/man8/cryptoboned.8.gz
%{_mandir}/man8/cryptobone.8.gz
%{_mandir}/man8/openpgp.8.gz
%{_mandir}/man8/cbcontrol.8.gz

%dir       %{_docdir}/%{name}
%dir       %{_datadir}/licenses/%{name}
%license   %{_datadir}/licenses/%{name}/COPYING
%license   %{_datadir}/licenses/%{name}/COPYING-cryptlib
%doc       %{_docdir}/%{name}/README
%doc       %{_docdir}/%{name}/README-cryptlib
%doc       %{_docdir}/%{name}/src-1.0.1.tgz

%changelog
* Fri Apr 8 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-11
- GUI update

* Fri Apr 8 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-10
- GUI update

* Fri Apr 8 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-10
- correct GUI initialization bug

* Sun Apr 3 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-9
- correct licenses directory in spec file, add help link in cryptobone GUI

* Tue Mar 29 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-8
- changed source of cryptoboned, relocated in /usr/lib/cryptobone/init.d
- moved COPYING to /usr/share/license/cryptobone

* Thu Mar 24 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-7
- updated spec file

* Fri Mar 18 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-6
- activation check in GUI

* Mon Mar 14 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-5
- replaced crontab entry by systemd timer file
- spec file changes: removed all service enable scripts
- spec file changes: made installation non-interactive

* Tue Mar  1 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-4
- updated spec file

* Mon Feb 22 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-3
- updated cron mechanism and systemd

* Sat Feb 20 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-2
- changed the installation process and updated spec file

* Fri Feb 19 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.1-1
- RC for Fedora package review with updated makefiles

* Sat Feb 13 2016 Senderek Web Security <innovation@senderek.ie> - 1.0-2
- update of cl343_beta.zip source code by Peter Gutmann
- removing all previous patches

* Sun Jan 24 2016 Senderek Web Security <innovation@senderek.ie> - 1.0-1
- Initial release of the first version ready for general use.

* Sat Jan 16 2016 Senderek Web Security <innovation@senderek.ie> - 0.99-3
- Security Update: introduction of the cryptobone daemon in version 0.99

* Sun Jul 26 2015 Senderek Web Security <innovation@senderek.ie>
- Initial RPM build
