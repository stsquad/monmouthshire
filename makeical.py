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
from argparse import ArgumentParser
from collections import namedtuple
from dateutil.parser import parse
from operator import attrgetter
from icalendar import Calendar, Event
from datetime import timedelta

import requests

LOCAL_INFO = "https://maps.monmouthshire.gov.uk/localinfo.aspx"

MyBins = namedtuple("MyBins", "Bins, Date")

def parse_arguments():
    """
    Read the arguments and return them to main.
    """
    # We need a unique building ID
    parser = ArgumentParser(description="Create .ical from Local Info.")
    parser.add_argument("uprn", metavar="N", type=int,
                        help="Your Unique Property Reference Number")
    parser.add_argument("--file", "-f", type=str, help="file to output")
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
    bins = []

    for w in waste_days:
        bin_type = w.find("h4").text
        bin_date = w.find("strong").text
        try:
            parsed_date = parse(bin_date)
            bins.append(MyBins(bin_type, parse(bin_date)))
        except ValueError:
            pass

    bins = sorted(bins, key=attrgetter("Date"))

    # and now we can construct the ical feed
    cal = Calendar()
    cal.add('prodid', '-//When the bins should be put out//mxm.dk//')
    cal.add('version', '2.0')

    # We want to put the bins out the evening before
    time_before = timedelta(hours=-6)
    time_duration = timedelta(minutes=30)

    for b in bins:
        e = Event()
        start = getattr(b, "Date") + time_before
        end = start + time_duration
        e.add('summary', "Put out %s" % (getattr(b, "Bins")))
        e.add('dtstart', start)
        e.add('dtend', end)
        cal.add_component(e)

    if args.file:
        f = open(args.file, 'wb')
        f.write(cal.to_ical())
    else:
        for b in bins:
            print ("Put out %s before %s" % (getattr(b, "Bins"), getattr(b, "Date")))
