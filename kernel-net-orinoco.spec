#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)
#
%define		_orinoco_rel	rc2
%define		_orinoco_name	orinoco
%define		_rel		0.%{_orinoco_rel}.2
Summary:	Linux driver for WLAN cards based on orinoco
Summary(pl.UTF-8):	Sterownik dla Linuksa do kart bezprzewodowych opartych na układzie orinoco
Name:		kernel-net-orinoco
Version:	0.15
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://www.ozlabs.org/people/dgibson/dldwd/%{_orinoco_name}-%{version}%{_orinoco_rel}.tar.gz
# Source0-md5:	2246f0879439d74f7aabc7935cec90c0
Patch0:		%{name}-makefile.patch
Patch1:		%{name}-pci.patch
URL:		http://www.nongnu.org/orinoco/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.7}
%{?with_dist_kernel:%requires_releq_kernel_up}
BuildRequires:	rpmbuild(macros) >= 1.153
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel}
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This is a Linux driver for WLAN cards based on orinoco.

This package contains Linux UP module.

%description -l pl.UTF-8
Sterownik dla Linuksa do kart bezprzewodowych opartych na układzie
orinoco.

Ten pakiet zawiera moduł jądra Linuksa UP.

%package -n kernel-smp-net-orinoco
Summary:	Linux SMP driver for WLAN cards based on orinoco
Summary(pl.UTF-8):	Sterownik dla Linuksa SMP do kart bezprzewodowych opartych na układzie orinoco
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel-smp}

%description -n kernel-smp-net-orinoco
This is a Linux driver for WLAN cards based on orinoco.

This package contains Linux SMP module.

%description -n kernel-smp-net-orinoco -l pl.UTF-8
Sterownik dla Linuksa do kart bezprzewodowych opartych na układzie
orinoco.

Ten pakiet zawiera moduł jądra Linuksa SMP.

%prep
%setup -q -n %{_orinoco_name}-%{version}%{_orinoco_rel}
%patch0 -p1
%patch1 -p1

%build
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/include/linux/version.h include/linux/version.h
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	for i in hermes orinoco_cs orinoco_nortel orinoco_pci orinoco_plx \
		orinoco_tmd orinoco spectrum_cs; do
		mv $i{,-$cfg}.ko
	done
done

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
for i in hermes orinoco_cs orinoco_nortel orinoco_pci orinoco_plx \
	orinoco_tmd orinoco spectrum_cs; do
install $i-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/$i.ko
done
%if %{with smp} && %{with dist_kernel}
for i in hermes orinoco_cs orinoco_nortel orinoco_pci orinoco_plx \
	orinoco_tmd orinoco spectrum_cs; do
install $i-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/$i.ko
done
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post -n kernel-smp-net-orinoco
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-net-orinoco
%depmod %{_kernel_ver}smp

%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-orinoco
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
