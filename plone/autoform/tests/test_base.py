# -*- coding: utf-8 -*-
from collections import OrderedDict
from plone.testing.zca import UNIT_TESTING

import unittest


class TestBase(unittest.TestCase):

    layer = UNIT_TESTING

    def test_calc_field_move_basics(self):
        from plone.autoform.base import AutoFields
        autofields = AutoFields()

        # we have a schema with fields [a, b, c]
        # field 'c' after 'a'
        order = [('c', 'after', 'a'), ]
        rules = autofields._calculate_field_moves(order)
        self.assertIn('a', rules)
        self.assertNotIn('c', rules)
        self.assertIn('with', rules['a'])
        self.assertIn('stub', rules['a'])
        self.assertIn('c', rules['a']['with'])
        self.assertIn('parent', rules['a']['with']['c'])
        self.assertIs(rules['a'], rules['a']['with']['c']['parent'])
        self.assertIn('target', rules['a']['with']['c'])
        self.assertIn('dir', rules['a']['with']['c'])

    def test_calc_field_move_simple_dependency(self):
        from plone.autoform.base import AutoFields
        autofields = AutoFields()

        # we have a schema with fields [a, b, c]
        # field a after b and field 'c' after 'a'
        order = [
            ('a', 'after', 'b'),
            ('c', 'after', 'a'),
        ]
        expected = {
            'stub': True,
            'with': OrderedDict(
                [
                    (
                        'a',
                        {
                            'with': OrderedDict(
                                [('c', {'target': 'a', 'dir': 'after'})]
                            ),
                            'target': 'b', 'dir': 'after'}
                    ),
                ]
            )
        }
        rules = autofields._calculate_field_moves(order)
        self.assertIn('b', rules)
        self.assertNotIn('a', rules)
        self.assertNotIn('c', rules)

        # remove parent key enable comparison of  dicts
        del rules['__all__']['a']['parent']
        del rules['__all__']['c']['parent']
        self.assertEqual(rules['b'], expected)

        # we have a schema with fields [a, b, c]
        # vice versa defined now, must lead to same result
        # field 'c' after 'a' and field a after b
        order = reversed(order)
        rules = autofields._calculate_field_moves(order)
        self.assertIn('b', rules)
        self.assertNotIn('a', rules)
        self.assertNotIn('c', rules)

        # remove parent key enable comparison of  dicts
        del rules['__all__']['a']['parent']
        del rules['__all__']['c']['parent']
        self.assertEqual(rules['b'], expected)

    def test_calc_field_move_multiple_dependencies(self):
        from plone.autoform.base import AutoFields
        autofields = AutoFields()

        order = [
            ('a', 'after', 'b'),
            ('c', 'after', 'a'),
            ('d', 'after', 'c'),
            ('z', 'after', 'x'),
            ('x', 'after', 'y'),
        ]
        rules = autofields._calculate_field_moves(order)
        self.assertIn('b', rules)
        self.assertIn('y', rules)
        self.assertNotIn('a', rules)
        self.assertNotIn('c', rules)
        self.assertNotIn('d', rules)
        self.assertNotIn('z', rules)
        self.assertNotIn('x', rules)

        self.assertIn('a', rules['b']['with'])
        self.assertEqual(1, len(rules['b']['with']))

        self.assertIn('c', rules['b']['with']['a']['with'])
        self.assertEqual(1, len(rules['b']['with']['a']['with']))

        self.assertIn('d', rules['b']['with']['a']['with']['c']['with'])
        self.assertEqual(1, len(rules['b']['with']['a']['with']['c']['with']))

    def test_calc_field_move_override(self):
        from plone.autoform.base import AutoFields
        autofields = AutoFields()

        order = [
            ('c', 'after', 'a'),
            ('a', 'after', 'b'),
            ('c', 'after', 'z'),
        ]
        rules = autofields._calculate_field_moves(order)
        self.assertIn('b', rules)
        self.assertIn('z', rules)
        self.assertNotIn('a', rules)
        self.assertNotIn('c', rules)
