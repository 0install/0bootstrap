import os, sys, tempfile, shutil, subprocess, textwrap

from zeroinstall.injector.config import load_config
from zeroinstall.injector import gpg

import support

_control_template = """Package: {deb_name}-launcher
Version: 1-1
Section: misc
Priority: optional
Architecture: all
Depends: zeroinstall-injector (>= 0.30)
Installed-Size: 1
Maintainer: {author}
{description}
 .
 Note: This is a launcher package; the actual program will be run using
 Zero Install.
 .
"""

def makedeb(config, iface):
	pkg_name = iface.get_name().lower().replace(' ', '-')

	desc_paras = ('Description: ' + iface.description).split('\n\n')
	wrapped = [textwrap.wrap(para) for para in desc_paras]
	desc_lines = []
	for para in wrapped:
		desc_lines += [' ' + (line or '.') for line in para]
	description = '\n'.join(desc_lines)[1:]

	sig, = config.iface_cache.get_cached_signatures(iface.uri)[:1]
	key = gpg.load_key(sig.fingerprint)

	control = _control_template.format(deb_name = pkg_name,
		   author = key.name,
		   description = description)

	d = tempfile.mkdtemp(prefix = 'bootstrap-')
	try:
		bin_dir = d + '/usr/bin'
		apps_dir = d + '/usr/share/applications'
		deb_dir = d + '/DEBIAN'
		os.makedirs(bin_dir)
		os.makedirs(apps_dir)
		os.makedirs(deb_dir)

		s = open(apps_dir + '/' + pkg_name + '.desktop', 'w')
		s.write(support.make_desktop_file(iface))
		s.close()

		s = open(deb_dir + '/control', 'w')
		s.write(control)
		s.close()

		subprocess.check_call(['fakeroot', 'dpkg-deb', '--build', '--', d, pkg_name + '.deb'])
	finally:
		shutil.rmtree(d)
