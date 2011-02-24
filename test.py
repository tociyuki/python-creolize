import sys
import unittest
from tests import test_10_creole
from tests import test_11_burnett
from tests import test_12_listadditions
from tests import test_13_larsch
from tests import test_20_heading
from tests import test_21_pholder
from tests import test_22_plugin
from tests import test_23_toc
from tests import test_30_django

def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_10_creole.TestCreolize('runTest'))
    suite.addTest(test_11_burnett.TestCreolize('runTest'))
    suite.addTest(test_12_listadditions.TestCreolize('runTest'))
    suite.addTest(test_13_larsch.TestCreolize('runTest'))
    suite.addTest(test_20_heading.TestCreolize('runTest'))
    suite.addTest(test_21_pholder.TestCreolize('runTest'))
    suite.addTest(test_22_plugin.TestCreolize('runTest'))
    suite.addTest(test_23_toc.TestCreolize('runTest'))
    suite.addTest(test_30_django.TestCreolize('runTest'))
    return suite

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=1).run(suite())
    sys.exit(not result.wasSuccessful())

