#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Create an .ical feed from the "Local Info" page

# Copyright (C) 2019 Alex Bennée <alex@bennee.com>
# Author: Alex Bennée <alex@bennee.com>
# URL: http://github.com/stsquad/monmouthshire.git
#
# Licensed under the GPLv3 or later, see LICENSE in top directory
#
# There doesn't seem to be an official feed but the data is all on the
# page so lets see if we can extract it. Mostly I just want the bin
# dates in my calender
#
#

from bs4 import BeautifulSoup
import requests
from argparse import ArgumentParser

LOCAL_INFO = "https://maps.monmouthshire.gov.uk/localinfo.aspx"

def parse_arguments():
    """
    Read the arguments and return them to main.
    """
    # We need a unique building ID
    parser = ArgumentParser(description="Create .ical from Local Info.")
    parser.add_argument("uprn", metavar="N", type=int,
                        help="Your Unique Property Reference Number")
    parser.add_argument("-f, --file", type=str, help="file to output")
    return parser.parse_args()

def fetch_info_page(uprn):
    """
    Fetch the bin dates from the Local Info pages
    """
    page = requests.get("%s?UniqueId=%d" % (LOCAL_INFO, uprn))
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

if __name__ == "__main__":
    args = parse_arguments()
    soup = fetch_info_page(args.uprn)
    waste_days = soup.select('div.waste.withExtraText')
    for w in waste_days:
        bin_type = w.find("h4").text
        bin_date = w.find("strong").text
        print ("Next %s on %s" % (bin_type, bin_date))
