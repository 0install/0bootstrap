import os, sys, tempfile, shutil, subprocess, tarfile, textwrap

from zeroinstall.injector.config import load_config
from zeroinstall.injector import gpg

import support

_spec_template = """
Summary: {summary}
Name: {rpm_name}-launcher
Version: 1
Release: 1
Group: Unknown
License: Unknown
Source: {rpm_name}.tar.gz
Prefix: /usr
BuildArch: noarch
Requires: zeroinstall-injector >= 0.30
Packager: {author}
%description
{description}

Note: This is a launcher package; the actual program will be run using
Zero Install.

%prep
%setup -c

%install
mkdir -p $RPM_BUILD_ROOT
cp -pR * $RPM_BUILD_ROOT

%files
#/usr/bin/*
/usr/share/applications/*.desktop
/usr/share/pixmaps/*.png
"""

def makerpm(config, iface, icon):
	rpm_name = iface.get_name().lower().replace(' ', '-')

	sig, = config.iface_cache.get_cached_signatures(iface.uri)[:1]
	key = gpg.load_key(sig.fingerprint)

	d = tempfile.mkdtemp(prefix = '0bootstrap-')
	try:
		os.environ['HOME'] = d
		bin_dir = d + '/usr/bin'
		apps_dir = d + '/usr/share/applications'
		icons_dir = d + '/usr/share/pixmaps'
		top_dir = d + '/rpmbuild'
		rpm_sources = top_dir + '/SOURCES'
		os.makedirs(bin_dir)
		os.makedirs(apps_dir)
		os.makedirs(icons_dir)
		os.makedirs(rpm_sources)
		os.makedirs(top_dir + '/BUILD')

		icon_name = None
		if icon:
			icon_name = rpm_name + '.png'
			shutil.copyfile(icon, icons_dir + '/' + icon_name)

		s = open(apps_dir + '/' + rpm_name + '.desktop', 'w')
		s.write(support.make_desktop_file(iface, icon_name))
		s.close()

		spec = _spec_template.format(rpm_name = rpm_name,
			   author = key.name,
			   summary = iface.summary,
			   description = iface.description,
			   TOPDIR = top_dir)

		s = open(d + '/' + rpm_name + '.spec', 'w')
		s.write(spec)
		s.close()

		t = tarfile.open(rpm_sources + '/' + rpm_name + '.tar.gz', 'w:gz')
		t.add(d + '/usr', 'usr', recursive=True)
		t.close()

		subprocess.check_call(['rpmbuild', '--define', '%_topdir ' + top_dir,
		                       '-bb', d + '/' + rpm_name + '.spec'])

		rpms_dir = top_dir + '/RPMS/noarch'
		rpm, = os.listdir(rpms_dir)
		shutil.copyfile(rpms_dir + '/' + rpm, './' + rpm_name + '.rpm')
	finally:
		shutil.rmtree(d)
