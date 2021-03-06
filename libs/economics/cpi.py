# -*- coding: utf-8 -*-

# cpi.py - Consumer Price Index data manipulation, computation and Class
# Copyright (C) 2013 Tryggvi Björgvinsson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import collections
import data
from datastructures import MapDict

class CPI(object):
    """
    Provides a Pythonic interface to Consumer Price Index data packages
    """

    def __init__(self, datapackage='http://data.okfn.org/data/cpi/',
                 country=None):
        """
        Initialise a CPI instance. Default data package location is the cpi
        data on http://data.okfn.org
        """

        # Store datapackage and country as instance variables
        self.datapackage = datapackage
        self.country = country

        # Initialise empty data structures
        self.data = MapDict()

        # Load the data into the data structures
        self.load()

    def load(self):
        """
        Load data with the data from the datapackage
        """

        # Loop through the rows of the datapackage with the help of data
        for row in data.get(self.datapackage):
            # Get the code and the name and transform to uppercase
            # so that it'll match no matter the case
            code = row['Country Code'].upper()
            name = row['Country Name'].upper()
            # Get the date (which is in the field Year) and the CPI value
            date = row['Year']
            cpi = row['CPI']
            
            # Try to get the data for country
            # or initialise an empty dict
            country_data = self.data.get(code, {})
            # Set the CPI value for the date
            country_data[date] = cpi

            # Set the code as the default key and name as extra
            # key in the mapdict for the country data
            self.data[(code, name)] = country_data

    def get(self, date=datetime.date.today(), country=None):
        """
        Get the CPI value for a specific time. Defaults to today. This uses
        the closest method internally but sets limit to one day.
        """
        try:
            return self.closest(date=date, country=country,
                                limit=datetime.timedelta(days=1))
        except:
            raise KeyError('Date {date} not found in data'.format(date=date))

    def closest(self, date=datetime.date.today(), country=None,
                limit=datetime.timedelta(days=366)):
        """
        Get the closest CPI value for a specified date. The date defaults to
        today. A limit can be provided to exclude all values for dates further
        away than defined by the limit. This defaults to 366 days.
        """

        # Try to get the country
        country = self.country if country is None else country

        # Get the data for the given country (we store it as uppercase)
        country_data = self.data[country.upper()]

        # Find the closest date
        closest_date = min(country_data.keys(),
                           key=lambda x: abs(date-x))
        
        # We return the CPI value if it's within the limit or raise an error
        if abs(date-closest_date) < limit:
            return collections.namedtuple('CPI', 'date value')\
                ._make((closest_date, country_data[closest_date]))
        else:
            raise KeyError('A date close enough was not found in data')
