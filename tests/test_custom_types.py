#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009, Nicolas Clairon
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

from mongokit import *

class CustomTypesTestCase(unittest.TestCase):
    def setUp(self):
        self.collection = Connection()['test']['mongokit']
        
    def tearDown(self):
        Connection()['test'].drop_collection('mongokit')

    def test_custom_type(self):
        import datetime

        class CustomDate(CustomType):
            mongo_type = unicode
            def to_bson(self, value):
                """convert type to a mongodb type"""
                return unicode(datetime.datetime.strftime(value,'%y-%m-%d'))
            def to_python(self, value):
                """convert type to a python object"""
                if value is not None:
                    return datetime.datetime.strptime(value, '%y-%m-%d')
                
        class Foo(MongoDocument):
            db_name = 'test'
            collection_name = 'mongokit'
            structure = {
                "date": CustomDate(),
            }
            default_values = {'date':u'08-06-07'}
            
        foo = Foo()
        foo['_id'] = 1
        foo['date'] = datetime.datetime(2003,2,1)
        foo.save()
        saved_foo =  foo.collection.find({'_id':1}).next()
        assert saved_foo == {u'date': u'03-02-01', u'_id': 1}
        foo.save()

        foo2 = Foo()
        foo2['_id'] = 2
        foo2.save()
        foo2.save()
        assert foo['date'] == datetime.datetime(2003,2,1), foo['date']
        foo = Foo.get_from_id(1)
        assert foo['date'] == datetime.datetime(2003,2,1), foo['date']
        saved_foo =  foo.collection.find({'_id':1}).next()
        assert saved_foo['date'] == CustomDate().to_bson(datetime.datetime(2003,2,1)), saved_foo['date']
        foo2 = Foo.get_from_id(2)
        assert foo2['date'] == datetime.datetime(2008,6,7), foo2

    def test_custom_type_nested(self):
        import datetime
        class CustomDate(CustomType):
            mongo_type = unicode
            def to_bson(self, value):
                """convert type to a mongodb type"""
                return unicode(datetime.datetime.strftime(value,'%y-%m-%d'))
            def to_python(self, value):
                """convert type to a python object"""
                if value is not None:
                    return datetime.datetime.strptime(value, '%y-%m-%d')
                
        class Foo(MongoDocument):
            db_name = 'test'
            collection_name = 'mongokit'
            structure = {
                'foo':{'date': CustomDate()},
            }
            default_values = {'foo.date':u'08-06-07'}
            
        foo = Foo()
        foo['_id'] = 1
        foo['foo']['date'] = datetime.datetime(2003,2,1)
        foo.save()
        foo.save()

        foo2 = Foo()
        foo2['_id'] = 2
        foo2.save()
        assert foo['foo']['date'] == datetime.datetime(2003,2,1), foo['foo']['date']
        foo = Foo.get_from_id(1)
        assert foo['foo']['date'] == datetime.datetime(2003,2,1)
        saved_foo =  foo.collection.find({'_id':1}).next()
        assert saved_foo['foo']['date'] == CustomDate().to_bson(datetime.datetime(2003,2,1)), foo['foo']['date']
        foo2 = Foo.get_from_id(2)
        assert foo2['foo']['date'] == datetime.datetime(2008,6,7), foo2

    def test_bad_custom_types(self):
        import datetime
        class CustomDate(CustomType):
            def to_bson(self, value):
                """convert type to a mongodb type"""
                return unicode(datetime.datetime.strftime(value,'%y-%m-%d'))
            def to_python(self, value):
                """convert type to a python object"""
                if value is not None:
                    return datetime.datetime.strptime(value, '%y-%m-%d')
                
        self.assertRaises(TypeError, CustomDate)

    def test_custom_type_nested_list(self):
        import datetime

        class CustomPrice(CustomType):
            mongo_type = float
            def to_bson(self, value):
                return float(value)
            def to_python(self, value):
                return str(value)

        class Receipt(MongoDocument):
            use_dot_notation = True
            db_name = 'test'
            collection_name = 'test'
            structure = {
                'products': [
                      {
                        'sku': unicode,
                        'qty': int,
                        'price': CustomPrice(),
                      }
                ]
            }
          
        r = Receipt()
        r['_id'] = 'bla'
        r.products = []
        r.products.append({ 'sku': u'X-25A5F58B-61', 'qty': 1, 'price': '9.99' })
        r.products.append({ 'sku': u'Z-25A5F58B-62', 'qty': 2, 'price': '2.99' })
        r.save()
        r_saved = r.collection.find_one({'_id':'bla'})
        assert r_saved == {u'_id': u'bla', u'products': [{u'sku': u'X-25A5F58B-61', u'price': 9.9900000000000002, u'qty': 1}, {u'sku': u'Z-25A5F58B-62', u'price': 2.9900000000000002, u'qty': 2}]}

    def test_custom_type_list(self):
        import datetime

        class CustomPrice(CustomType):
            mongo_type = float
            python_type = basestring
            def to_bson(self, value):
                print "blaaa"
                return float(value)
            def to_python(self, value):
                return str(value)

        class Receipt(MongoDocument):
            db_name = 'test'
            collection_name = 'test'
            structure = {
                'foo': CustomPrice(),
                'price': [CustomPrice()],
                'bar':{'spam':CustomPrice()},
            }
          
        r = Receipt()
        r['_id'] = 'bla'
        r['foo'] = '2.23'
        r['price'].append('9.99')
        r['price'].append('2.99')
        r['bar']['spam'] = '3.33'
        r.save()
        r_saved = r.collection.find_one({'_id':'bla'})
        assert r_saved == {u'price': [9.9900000000000002, 2.9900000000000002], u'_id': u'bla', u'bar': {u'spam': 3.3300000000000001}, u'foo': 2.23}
