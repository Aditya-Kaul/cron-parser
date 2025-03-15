#!/usr/bin/env python3
import unittest
import sys
from io import StringIO
from unittest.mock import patch

from app import (
    expand_cron_exp, 
    CronExpression, 
    RawCronExpression, 
    expand_expression, 
    TableOutput
)

class TestExpandExpression(unittest.TestCase):

    def test_asterisk(self):
        options = list(range(1, 6))
        result = expand_expression("*", options)
        self.assertEqual(result, options)
    
    def test_single_value(self):
        options = list(range(1, 6))
        result = expand_expression("3", options)
        self.assertEqual(result, [3])
    
    def test_comma_separated_values(self):
        options = list(range(1, 6))
        result = expand_expression("1,3,5", options)
        self.assertEqual(result, [1, 3, 5])
    
    def test_range(self):
        options = list(range(1, 6))
        result = expand_expression("2-4", options)
        self.assertEqual(result, [2, 3, 4])
        
    
    def test_interval(self):
        """Test that */n expands to every nth value."""
        options = list(range(1, 10))
        result = expand_expression("*/2", options)
        self.assertEqual(result, [1, 3, 5, 7, 9])
    
    def test_range_with_interval(self):
        options = list(range(1, 10))
        result = expand_expression("2-8/2", options)
        self.assertEqual(result, [2, 4, 6, 8])
    
    def test_invalid_value(self):
        options = list(range(1, 6))
        with self.assertRaises(ValueError):
            expand_expression("10", options)
    
    def test_invalid_range(self):
        options = list(range(1, 6))
        with self.assertRaises(ValueError):
            expand_expression("5-2", options)
    
    def test_invalid_interval(self):
        options = list(range(1, 6))
        with self.assertRaises(ValueError):
            expand_expression("*/0", options)
    
    def test_unrecognized_format(self):
        options = list(range(1, 6))
        with self.assertRaises(ValueError):
            expand_expression("a", options)


class TestCronExpression(unittest.TestCase):
    
    def test_init(self):
        cron = CronExpression("0 0 1 1 1 /usr/bin/command")
        self.assertEqual(cron.minute, [0])
        self.assertEqual(cron.hour, [0])
        self.assertEqual(cron.day_of_month, [1])
        self.assertEqual(cron.month, [1])
        self.assertEqual(cron.day_of_week, [1])
        self.assertEqual(cron.command, "/usr/bin/command")
    
    def test_init_with_complex_expression(self):
        cron = CronExpression("*/5 0-12 1,15 */2 1-5 /usr/bin/complex")
        self.assertEqual(cron.minute, [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        self.assertEqual(cron.hour, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertEqual(cron.day_of_month, [1, 15])
        self.assertEqual(cron.month, [1, 3, 5, 7, 9, 11])
        self.assertEqual(cron.day_of_week, [1, 2, 3, 4, 5])
        self.assertEqual(cron.command, "/usr/bin/complex")
    
    def test_to_table_format(self):
        cron = CronExpression("0 0 1 1 1 /usr/bin/command")
        table = cron.to_table_format()
        self.assertEqual(len(table), 6)
        self.assertEqual(table[0], ("minute", [0]))
        self.assertEqual(table[5], ("command", "/usr/bin/command"))
    
    def test_invalid_expression(self):
        with self.assertRaises(ValueError):
            CronExpression("0 0 1 1")  # Missing parts


class TestRawCronExpression(unittest.TestCase):
    """Test the RawCronExpression class."""
    
    def test_init(self):
        cron = RawCronExpression("0 0 1 1 1 /usr/bin/command")
        self.assertEqual(cron.minute, "0")
        self.assertEqual(cron.hour, "0")
        self.assertEqual(cron.day_of_month, "1")
        self.assertEqual(cron.month, "1")
        self.assertEqual(cron.day_of_week, "1")
        self.assertEqual(cron.command, "/usr/bin/command")
    
    def test_expand(self):
        raw = RawCronExpression("*/5 0-12 1,15 */2 1-5 /usr/bin/complex")
        expanded = raw.expand()
        self.assertEqual(expanded.minute, [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        self.assertEqual(expanded.hour, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.assertEqual(expanded.day_of_month, [1, 15])
        self.assertEqual(expanded.month, [1, 3, 5, 7, 9, 11])
        self.assertEqual(expanded.day_of_week, [1, 2, 3, 4, 5])
        self.assertEqual(expanded.command, "/usr/bin/complex")
    
    def test_invalid_expression(self):
        with self.assertRaises(ValueError):
            RawCronExpression("0 0 1 1")  

class TestExpandCronExp(unittest.TestCase):
    
    def test_simple_expression(self):
        result = expand_cron_exp("0 0 1 1 1 /usr/bin/command")
        expected = "minute         0\nhour           0\nday of month   1\nmonth          1\nday of week    1\ncommand        /usr/bin/command"
        self.assertEqual(result, expected)
    
    def test_complex_expression(self):
        """Test a complex cron expression."""
        result = expand_cron_exp("*/5 0-12 1,15 */2 1-5 /usr/bin/complex")
        self.assertIn("minute         0 5 10 15 20 25 30 35 40 45 50 55", result)
        self.assertIn("hour           0 1 2 3 4 5 6 7 8 9 10 11 12", result)
        self.assertIn("day of month   1 15", result)
        self.assertIn("month          1 3 5 7 9 11", result)
        self.assertIn("day of week    1 2 3 4 5", result)
        self.assertIn("command        /usr/bin/complex", result)
    
    def test_command_with_arguments(self):
        result = expand_cron_exp("0 0 1 1 1 /usr/bin/command -a -b --c=d")
        self.assertIn("command        /usr/bin/command -a -b --c=d", result)
    
    def test_invalid_expression(self):
        """Test that an invalid expression raises a ValueError."""
        with self.assertRaises(ValueError):
            expand_cron_exp("0 0 1 1")  # Missing parts


class TestMain(unittest.TestCase):
    
    @patch('sys.argv', ['app.py', '0 0 1 1 1 /usr/bin/command'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_success(self, mock_stdout):
        from app import main
        main()
        self.assertIn("minute         0", mock_stdout.getvalue())
        self.assertIn("command        /usr/bin/command", mock_stdout.getvalue())
    
    @patch('sys.argv', ['app.py'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_no_args(self, mock_stdout):
        from app import main
        with self.assertRaises(SystemExit):
            main()
        self.assertIn("Usage:", mock_stdout.getvalue())
    
    @patch('sys.argv', ['app.py', '0 0 1 1'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_invalid_expression(self, mock_stdout):
        from app import main
        with self.assertRaises(SystemExit):
            main()
        self.assertIn("Error:", mock_stdout.getvalue())


if __name__ == '__main__':
    unittest.main()