#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import sys

if not '..' in sys.path:
    sys.path.insert(0, '..')

import argparse
import unittest

from perceval.backend import BackendCommand


class TestBackendCommand(unittest.TestCase):

    def test_parsing_on_init(self):
        """Test if the arguments are parsed when the class is initialized"""

        args = ['-u', 'jsmith', '-p', '1234', '-t', 'abcd',
                '--from-date', '2015-01-01']

        cmd = BackendCommand(*args)

        self.assertIsInstance(cmd.parsed_args, argparse.Namespace)
        self.assertEqual(cmd.parsed_args.backend_user, 'jsmith')
        self.assertEqual(cmd.parsed_args.backend_password, '1234')
        self.assertEqual(cmd.parsed_args.backend_token, 'abcd')
        self.assertEqual(cmd.parsed_args.from_date, '2015-01-01')

    def test_argument_parser(self):
        """Test if it returns a argument parser object"""

        parser = BackendCommand.create_argument_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)


if __name__ == "__main__":
    unittest.main()
