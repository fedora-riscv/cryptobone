%global cryptobonedir %{_prefix}/lib/%{name}
%global _hardened_build 1

Name:       cryptobone
Version:    1.4   
Release:    1%{?dist}
Summary:    Secure Communication Under Your Control      

License:    BSD and Sleepycat and OpenSSL     
URL:        https://crypto-bone.com      
Source0:    https://crypto-bone.com/release/source/cryptobone-%{version}.tar.gz       
Source1:    https://crypto-bone.com/release/source/cryptobone-%{version}.tar.gz.asc
Source2:    gpgkey-3274CB29956498038A9C874BFBF6E2C28E9C98DD.asc

ExclusiveArch: x86_64 ppc64le aarch64

BuildRequires: libbsd-devel
BuildRequires: gcc
BuildRequires: gnupg2
BuildRequires: desktop-file-utils
BuildRequires: systemd
BuildRequires: make
BuildRequires: libmd-devel

Requires: systemd
Requires: bash    
Requires: python3
Requires: python3-tkinter
Requires: openssh-askpass
Requires: fetchmail
Requires: coreutils
Requires: rng-tools
Requires: MTA 
Requires: socat
Requires: cryptsetup
Requires: openssh
Requires: nmap
Requires: polkit

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
mkdir -p .gnupg
gpg2 --homedir .gnupg --no-default-keyring --quiet --yes --output $KEYRING --dearmor  %{SOURCE2}
gpg2 --homedir .gnupg --no-default-keyring --keyring $KEYRING --verify %{SOURCE1} %{SOURCE0}
%setup 

%build
%configure
echo OPTFLAGS: %{optflags}
make %{?_smp_mflags} ADDFLAGS="%{optflags}"

%install
%make_install
mkdir -p %{buildroot}%{_datadir}/icons/default
cp %{buildroot}%{cryptobonedir}/GUI/cryptobone.png %{buildroot}%{_datadir}/icons/default
cp %{buildroot}%{cryptobonedir}/GUI/external-cryptobone-admin.png %{buildroot}%{_datadir}/icons/default
desktop-file-install --dir %{buildroot}%{_datadir}/applications -m 644 %{buildroot}%{cryptobonedir}/GUI/cryptobone.desktop
desktop-file-install --dir %{buildroot}%{_datadir}/applications -m 644 %{buildroot}%{cryptobonedir}/GUI/external-cryptobone-admin.desktop

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
     systemctl stop cryptoboneexternd
     systemctl disable cryptoboneexternd
     systemctl disable cryptobone-fetchmail.timer
     systemctl stop cryptobone-fetchmail.timer
     umount %{cryptobonedir}/keys 2> /dev/null
     rm -f /etc/sudoers.d/cbcontrol
     if [ -f %{cryptobonedir}/bootswitch ] ; then
          chattr -i %{cryptobonedir}/bootswitch
     fi
     rm -rf /dev/shm/RAM 2>/dev/null
     rm -rf /dev/shm/EXRAM 2>/dev/null
     /usr/sbin/userdel cryptobone
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
if grep cryptobone /etc/passwd >/dev/null 2>/dev/null; then
     # update permissions on cryptobone's home directory and shell
     chown cryptobone %{cryptobonedir} %{cryptobonedir}/ext
     chown cryptobone %{cryptobonedir}/ext/cryptoboneshell
fi


%files
%{_unitdir}/cryptoboned.service
%{_unitdir}/cryptobone-dbinit.service
%{_unitdir}/cryptoboneexternd.service
%{_unitdir}/cryptobone-fetchmail.service
%{_unitdir}/cryptobone-fetchmail.timer
%{_bindir}/activate-cryptobone
%{_bindir}/cryptobone
%{_bindir}/external-cryptobone
%{_bindir}/external-cryptobone-admin

# The directory %%{cryptobonedir} contains security-critical files that need to be
# protected from being accessed by non-root users. In addition to restricting the
# main cryptobone directory to root-access, certain files will also have 0700 mode
# to ensure that they are protected even if (accidentally) the directory permission
# might be changed. In particular, this is crucial for the keys subdirectory.
%{cryptobonedir}

%{_datadir}/applications/cryptobone.desktop
%{_datadir}/applications/external-cryptobone-admin.desktop
%{_datadir}/icons/default/cryptobone.png
%{_datadir}/icons/default/external-cryptobone-admin.png

%{_mandir}/man8/cryptoboned.8.gz
%{_mandir}/man8/cryptobone.8.gz
%{_mandir}/man8/activate-cryptobone.8.gz
%{_mandir}/man8/external-cryptobone-admin.8.gz
%{_mandir}/man8/external-cryptobone.8.gz
%{_mandir}/man8/cbcontrol.8.gz

%license   %{_datadir}/licenses/%{name}/COPYING
%license   %{_datadir}/licenses/%{name}/COPYING-cryptlib
%doc       %{_docdir}/%{name}/README
%doc       %{_docdir}/%{name}/README-cryptlib

%changelog
* Fri Feb 03 2023 Ralf Senderek <innovation@senderek.ie> - 1.4-1
- Resolved [Bug 2166632]

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Mon Nov 28 2022 Ralf Senderek <innovation@senderek.ie> - 1.3-10
- Fix dependency change

* Wed Jul 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Tue Mar 08 2022 Ralf Senderek <innovation@senderek.ie> - 1.3-8
- use arch x86-64-v3 instead of native

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri Jun 25 2021 Ralf Senderek <innovation@senderek.ie> - 1.3-5
- Fix pthread issue

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jan 23 2020 Ralf Senderek <innovation@senderek.ie> - 1.3-1
- Prepared for gcc 10

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Apr 11 2019 Ralf Senderek <innovation@senderek.ie> - 1.2-1
- Update all scripts to python3 and using new cryptlib-3.4.5 reduced library

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Sep 24 2018 Ralf Senderek <innovation@senderek.ie> - 1.1.2-5
- Force python2 execution of scripts

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Mar 13 2018 Iryna Shcherbina <ishcherb@redhat.com> - 1.1.2-3
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Aug 12 2017 Senderek Web Security <innovation@senderek.ie> - 1.1.2-1
- support for aarch64 and powerpc64

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 05 2017 Senderek Web Security <innovation@senderek.ie> - 1.1.1-6
- exclude aarch64

* Sun Feb 19 2017 Senderek Web Security <innovation@senderek.ie> - 1.1.1-5
- mandatory rebuild, no changes

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 31 2017 Senderek Web Security <innovation@senderek.ie> - 1.1.1-3
- compile with gcc-7.0 and -march=native

* Tue Dec 13 2016 Senderek Web Security <innovation@senderek.ie> - 1.1.1-2
- compile initdatabase.c with PIE

* Sun Dec 04 2016 Senderek Web Security <innovation@senderek.ie> - 1.1.1-1
- switch from retired beesu to polkit in GUI code

* Tue Nov 08 2016 Senderek Web Security <innovation@senderek.ie> - 1.1.0-2
- enable bidirectional ssh in firewall script to support IP scan

* Sat Nov 05 2016 Senderek Web Security <innovation@senderek.ie> - 1.1.0-1
- full redesign of the GUI
- update selinux module for external cryptobone
- add cryptobone-dbinit.service unit with CRYPT_RANDOM_SLOWPOLL

* Mon Sep 05 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.6-3
- fix bug in daemon start script
- rename signed source file

* Mon Sep 05 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.6-2
- substitute ksh by bash
- remove obsolete dependencies

* Sat Aug 27 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.6-1
- adding the external cryptobone daemon
- remove conflict tag, as external cryptobone code is now distributed in this package

* Tue Aug 02 2016 Senderek Web Security <innovation@senderek.ie> - 1.0.5-1
- correct license tag (RHBZ #1352406)
- rename cryptlib symbols (RHBZ #1352404)
- use base64encode and base64decode from cryptlib code
- reduce cryptlib code in the private library libclr.so
- move message encryption code inside the cryptobone daemon, remove openpgp binary
- extend secrets data base

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
