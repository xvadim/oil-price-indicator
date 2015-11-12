#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Vadym Khokhlov <Vadym Khokhlov@Vadims-MacBook-Pro.local>
#
# Distributed under terms of the MIT license.

from lxml import etree
from json import dumps

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import webapp2

OLD_PRICE_ID = 'oldPriceKey'

ICON_UP = "i120"
ICON_DOWN = "i124"
ICON_EQ = "i401"  # the  '=' icon


class Price(ndb.Model):
    value = ndb.FloatProperty()
    client_addr = ndb.StringProperty()

    @classmethod
    def oldPrice(cls, client_addr):
        res = Price.query(Price.client_addr == client_addr).fetch(1)
        if len(res) == 0:
            oldValue = Price(value=50.0, client_addr=client_addr)
        else:
            oldValue = res[0]
        return oldValue


class MainPage(webapp2.RequestHandler):
    def get(self):
        price = self.newPrice()
        oldPrice = Price.oldPrice(self.request.remote_addr)

        icon = ICON_EQ
        if oldPrice.value > price:
            icon = ICON_DOWN
        elif oldPrice.value < price:
            icon = ICON_UP

        oldPrice.value = price
        oldPrice.put()

        data = {
            "frames": [
                {
                    "index": 0,
                    "text": "%.2f$" % price,
                    "icon": icon
                    },
                {
                    "index": 1,
                    "text": "%.2f$" % price,
                    "icon": "i1819"
                }
                ]
            }

        self.response.headers['Content-Type'] = 'Application/json'
        self.response.write(dumps(data))

    def newPrice(self):
        result = urlfetch.fetch('http://bloomberg.com/energy/')
        tree = etree.HTML(result.content)
        prices = tree.xpath('//td[@class="data-table__row__cell"][@data-type="value"]/text()')
        return float(prices[1])

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
