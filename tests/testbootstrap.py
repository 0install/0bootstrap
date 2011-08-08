import subprocess, tempfile, os
from StringIO import StringIO
import unittest

from zeroinstall.support import ro_rmtree

bootstrap = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '0bootstrap')

def run(args, **kwargs):
	child = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	got, unused = child.communicate()
	code = child.wait()
	if code != kwargs.get('expect_status', 0):
		raise Exception("Exit status %d:\n%s" % (code, got))

	expected = kwargs.get('expect', '')
	if expected:
		if expected.lower() not in got.lower():
			raise Exception("Expected '%s', got '%s'" % (expected, got))
	elif got:
		raise Exception("Expected nothing, got '%s'" % got)

class TestBootstrap(unittest.TestCase):
	def setUp(self):
		self.tmpdir = tempfile.mkdtemp(prefix = '0bootstrap-test-')
		os.chdir(self.tmpdir)

	def tearDown(self):
		ro_rmtree(self.tmpdir)
	
	def testDeb(self):
		run([bootstrap, "--browser=Ubuntu/10.04", "http://rox.sourceforge.net/2005/interfaces/ROX-Filer"],
				expect = "dpkg-deb: building package `rox-filer-launcher' in `rox-filer.deb'")

	def testRPM(self):
		run([bootstrap, "--browser=Red Hat", "http://rox.sourceforge.net/2005/interfaces/ROX-Filer"],
				expect = "Processing files: rox-filer-launcher-1-1.noarch")

suite = unittest.makeSuite(TestBootstrap)
if __name__ == '__main__':
	unittest.main()
