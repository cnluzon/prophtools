# -*- coding: utf-8 -*-

import unittest
import os
import tempfile
import shutil
import prophtools.utils.validation as validation
import prophtools.utils.loggingtools as loggingtools
import logging

class TestValidationFunctions(unittest.TestCase):
    """
    Test for validation functions
    """

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.tempfile = os.path.join(self.tempdir, 'test.txt')
        fo = open(self.tempfile, 'w')
        fo.close()
        tmp_log = os.path.join(self.tempdir, 'validation.log')
        loggingtools.init_generic_log(tmp_log, 2)
        self.log = logging.getLogger()

    def tearDown(self):
        """Function to do cleaning up after the test."""
        shutil.rmtree(self.tempdir)

    def test_log_level_debug(self):
        self.assertEqual(loggingtools.get_logging_level(2), logging.DEBUG)

    def test_log_level_info(self):
        self.assertEqual(loggingtools.get_logging_level(1), logging.INFO)

    def test_log_level_warning(self):
        self.assertEqual(loggingtools.get_logging_level(0), logging.WARNING)

    def test_file_exists_true_when_file_exists(self):
        self.assertTrue(validation.check_file_exists(self.tempfile))

    def test_file_exists_false_when_file_doesnt_exist(self):
        not_a_file = os.path.join(self.tempdir, 'nohay.txt')
        self.assertFalse(validation.check_file_exists(not_a_file, self.log))

    def test_try_to_open_file_opens(self):
        validation.try_to_open_file(self.tempfile, self.log)

    def test_try_to_open_not_a_file_returns_false(self):
        not_a_file = os.path.join(self.tempdir, 'nohay.txt')
        result = validation.try_to_open_file(not_a_file, self.log)
        self.assertFalse(result)

    def test_verify_natural_number_normal_case(self):
        self.assertTrue(validation.verify_natural_number(10, 'n', self.log))

    def test_verify_numerical_value_over_normal_case(self):
        self.assertTrue(validation.verify_numeric_value_over_value(20, 'v', 10,
                                                                   self.log))

    def test_verify_numerical_value_over_not_valid_returns_false(self):
        self.assertFalse(validation.verify_numeric_value_over_value(10, 'v', 15, self.log))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestValidationFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
