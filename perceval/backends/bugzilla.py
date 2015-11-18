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
#     Alvaro del Castillo San Felix <acs@bitergia.com>
#

import csv
import datetime

import requests

from ..utils import DEFAULT_DATETIME, str_to_datetime


class Bugzilla:
    """Bugzilla backend.

    This class allows the fetch the bugs stored in Bugzilla
    repository. To initialize this class the URL of the server
    must be provided.

    :param url: Bugzilla server URL
    """
    def __init__(self, url):
        self.url = url
        self.client = BugzillaClient(url)

    def fetch(self, from_date=DEFAULT_DATETIME):
        """Fetch the bugs from the repository.

        The method retrieves, from a Bugzilla repository, the bugs
        updated since the given date.

        :param from_date: obtain bugs updated since this date
        """
        buglist = self.__fetch_buglist(from_date)

        return [bug for bug in buglist]

    def __fetch_buglist(self, from_date):
        buglist = self.__fetch_and_parse_buglist_page(from_date)

        while buglist:
            bug = buglist.pop(0)
            last_date = bug['changeddate']
            yield bug

            # Bugzilla does not support pagination. Due to this,
            # the next list of bugs is requested adding one second
            # to the last date obtained.
            if not buglist:
                from_date = str_to_datetime(last_date)
                from_date += datetime.timedelta(seconds=1)
                buglist = self.__fetch_and_parse_buglist_page(from_date)

    def __fetch_and_parse_buglist_page(self, from_date):
        raw_csv = self.client.buglist(from_date=from_date)
        buglist = self.__parse_buglist(raw_csv)
        return [bug for bug in buglist]

    def __parse_buglist(self, raw_csv):
        reader = csv.DictReader(raw_csv.split('\n'),
                                delimiter=',', quotechar='"')
        for row in reader:
            yield row


class BugzillaClient:
    """Bugzilla API client.

    This class implements a simple client to retrieve distinct
    kind of data from a Bugzilla repository. Currently, it only
    supports 3.x and 4.x servers.

    :param base_url: URL of the Bugzilla server
    """

    URL = "%(base)s/%(cgi)s"
    HEADERS = {'User-Agent': 'perceval-bg-0.1'}

    # Bugzilla versions that follow the old style queries
    OLD_STYLE_VERSIONS = ['3.2.3', '3.2.2']

    # CGI methods
    CGI_BUGLIST = 'buglist.cgi'
    CGI_BUG = 'show_bug.cgi'
    CGI_BUG_ACTIVITY = 'show_activity.cgi'

    # CGI params
    PBUG_ID= 'id'
    PCHFIELD_FROM = 'chfieldfrom'
    PCTYPE = 'ctype'
    PORDER = 'order'
    PEXCLUDE_FIELD = 'excludefield'

    # Content-type values
    CTYPE_CSV = 'csv'
    CTYPE_XML = 'xml'


    def __init__(self, base_url):
        self.base_url = base_url

    def metadata(self):
        """Get metadata information in XML format."""

        params = {
            self.PCTYPE : self.CTYPE_XML
        }

        response = self.call(self.CGI_BUG, params)

        return response

    def buglist(self, from_date=DEFAULT_DATETIME, version=None):
        """Get a summary of bugs in CSV format.

        :param from_date: retrieve bugs that where updated from that date
        :param version: version of the server
        """
        if version in self.OLD_STYLE_VERSIONS:
            order = 'Last+Changed'
        else:
            order = 'changeddate'

        date = from_date.strftime("%Y-%m-%dT%H:%M:%S")

        params = {
            self.PCHFIELD_FROM : date,
            self.PCTYPE : self.CTYPE_CSV,
            self.PORDER : order
        }

        response = self.call(self.CGI_BUGLIST, params)

        return response

    def bugs(self, *bug_ids):
        """Get the information of a list of bugs in XML format.

        :param bug_ids: list of bug identifiers
        """
        params = {
            self.PBUG_ID : bug_ids,
            self.PCTYPE : self.CTYPE_XML,
            self.PEXCLUDE_FIELD : 'attachmentdata'
        }

        response = self.call(self.CGI_BUG, params)

        return response

    def bug_activity(self, bug_id):
        """Get the activity of a bug in HTML format.

        :param bug_id: bug identifier
        """
        params = {
            self.PBUG_ID : bug_id
        }

        response = self.call(self.CGI_BUG_ACTIVITY, params)

        return response

    def call(self, cgi, params):
        """Run an API command.

        :param cgi: cgi method to run on the server
        :param params: dict with the HTTP parameters needed to run
            the given method
        """
        url = self.URL % {'base' : self.base_url, 'cgi' : cgi}

        req = requests.get(url, params=params,
                           headers=self.HEADERS)
        req.raise_for_status()

        return req.text