%global cryptobonedir %{_prefix}/lib/%{name}
%global _hardened_build 1

Name:       cryptobone
Version:    1.0.3   
Release:    1%{?dist}
Summary:    Secure Communication Under Your Control      

Group:      Applications/Internet         
License:    BSD and MIT     
URL:        https://crypto-bone.com      
Source0:    https://crypto-bone.com/release/source/cryptobone-%{version}-1.tar.gz       
Source1:    https://crypto-bone.com/release/source/cryptobone-%{version}-1.tar.gz.asc
Source2:    gpgkey-3274CB29956498038A9C874BFBF6E2C28E9C98DD.asc


ExclusiveArch: x86_64 %{ix86} %{arm}

BuildRequires: libbsd-devel
BuildRequires: gcc
BuildRequires: gnupg2
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

# If a second Linux computer is used to store the encrypted message keys,
# this system must use cryptobone-extern instead of cryptobone.
Conflicts: cryptobone-extern


%description
The Crypto Bone is a secure messaging system that makes sure a user's
email is always encrypted without burdening the user with the message
key management. Based on a GUI and a separate daemon, both ease-of-use
and security are assured by a novel approach to encryption key management.

While the message keys are secured by a daemon running on the Linux machine,
additional protection can be achieved by using an external device for storing
encryption keys. This external device can be another Linux computer dedicated
to this task or a Beagle Bone or a Raspberry Pi.  (https://crypto-bone.com)

# The cryptobone package uses the cryptlib library as a private library.
# As the cryptobone is based on only a very small part of cryptlib,
# essentially the symmetric encryption enveloping only, and because the
# reduction of complexity is one of cryptobone's main goals, the 
# software links to a reduced, minimalistic version of cryptlib.
# Because the fully-fledged cryptlib uses the the name libcl.so this
# reduced cryptlib uses a different name (libclr.so) to avoid confusion.


%prep
KEYRING=$(echo %{SOURCE2})
KEYRING=${KEYRING%%.asc}.gpg
gpg2 --no-default-keyring --quiet --yes --output $KEYRING --dearmor  %{SOURCE2}
gpg2 --no-default-keyring --keyring $KEYRING --verify %{SOURCE1} %{SOURCE0}
%setup 


%build
%configure
echo OPTFLAGS: %{optflags}
make %{?_smp_mflags} ADDFLAGS="%{optflags}"

%install
%make_install
mkdir -p %{buildroot}%{_datadir}/icons/default
cp %{buildroot}%{cryptobonedir}/GUI/cryptobone.png %{buildroot}%{_datadir}/icons/default
desktop-file-install --dir %{buildroot}%{_datadir}/applications -m 644 %{buildroot}%{cryptobonedir}/GUI/cryptobone.desktop


%post
# this script is run after the packet's installation 
if [ $1 -eq 1 ] ; then
     # installation only, not running after update
     if [ -x /usr/sbin/semodule ]; then
          # only if SELinux is installed, prepare cryptobone.pp
          /usr/sbin/semodule -i /usr/lib/cryptobone/selinux/cryptobone.pp
          /usr/sbin/semodule -e cryptobone
     fi
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
     if [ -x /usr/sbin/semodule ]; then
          semodule -d cryptobone
     fi
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

%license   %{_datadir}/licenses/%{name}/COPYING
%license   %{_datadir}/licenses/%{name}/COPYING-cryptlib
%doc       %{_docdir}/%{name}/README
%doc       %{_docdir}/%{name}/README-cryptlib
%doc       %{_docdir}/%{name}/src-1.0.3.tgz

%changelog

* Fri May 6 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.3-1
- extending $RPM_OPT_FLAGS to private cryptlib 
- adding three patches to cryptlib source code, approved by Peter Gutmann
- adding GPG source code signature check

* Sun Apr 24 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.2-3
- update source code 

* Sun Apr 24 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.2-2
- fixes bug #1329695 (cryptobone is not built with $RPM_OPT_FLAGS)
- updates cryptobone.png and SELinux policy

* Sat Apr 16 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.2-1
- upgrade to cryptlib-3.4.3 final
- removing all brainpool crypto code from the cryptlib source code
- renaming the private cryptlib library to libclr.so
- adding basic SELinux support

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
