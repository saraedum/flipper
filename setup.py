
from __future__ import print_function
from distutils.core import setup, Command
import importlib

# Get the correct version.
from version import flipper_version

# So we can access all of the test suite just by doing 'python setup.py test'
class TestCommand(Command):
	description = 'Runs all tests in the tests directory.'
	user_options = []
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		''' Runs all of the tests in the tests directory. '''
		print(self.verbose)
		try:
			test_module = importlib.import_module('flipper.tests')
		except ImportError:
			print('flipper module unavailable, install by running: \n>>> python setup.py install [--user]')
		else:
			failed_tests = []
			for test_name in dir(test_module):
				if not test_name.startswith('_') and test_name != 'flipper':
					test = importlib.import_module('flipper.tests.%s' % test_name)
					print('Running %s test...' % test_name)
					result = test.main()
					print('\tPassed' if result else '\tFAILED')
					if not result:
						failed_tests.append(test_name)
			
			print('Finished testing.')
			if len(failed_tests) > 0:
				print('\tFAILED TESTS:')
				for test_name in failed_tests:
					print('\t%s' % test_name)
			else:
				print('\tAll tests passed.')

setup(
	name='flipper',
	version=flipper_version,
	description='flipper',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/flipper',
	packages=['flipper'],
	package_dir={'flipper':''},
	# Remember to update these if the directory structure changes.
	package_data={'flipper':['application/*.py', 'application/icon/*', 'application/docs/*', 'examples/*.py', 'kernel/*.py', 'tests/*.py', 'profile/*.py', 'docs/*', 'version.py']},
	cmdclass={'test':TestCommand}
	)
