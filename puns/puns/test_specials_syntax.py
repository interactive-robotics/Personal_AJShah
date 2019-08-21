#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 16:35:44 2019

@author: ajshah
"""

import unittest
from puns.FormulaTools import *

class TestSpecialSyntax(unittest.TestCase):

    def test_cosafe_atom(self):
        formula = ['a']
        (flag,sub) = IsCoSafe(formula)
        print('Testing cosafety, atomic: Pass 1')
        self.assertTrue(flag)

    def test_cosafe_out_of_grammar(self):
        formula = ['G',['a']]
        (flag,sub) = IsCoSafe(formula)
        print('Testing cosafety, bad operators: Fail 1')
        self.assertFalse(flag)
        self.assertEqual(sub, ['G',['a']])

    def test_cosafe_bad_subformula_not(self):
        formula = ['not',['F',['a']]]
        print('Testing cosafety, bad subformula for not: Fail 2')
        (flag,sub) = IsCoSafe(formula)
        self.assertFalse(flag)
        self.assertEqual(sub,['F',['a']])

    def test_cosafe_not(self):
        formula = ['not',['a']]
        print('Testing cosafety, not: Pass')
        flag,sub = IsCoSafe(formula)
        self.assertTrue(flag)

    def test_cosafe_bad_syntax(self):
        formula = ['a','a']
        print('Testing cosafety, bad syntax: Fail 3')
        flag,sub = IsCoSafe(formula)
        self.assertFalse(flag)
        self.assertEqual(sub,['a','a'])

    def test_cosafe_implication_pass(self):
        formula = ['imp',['a'],['b']]
        print('Testing cosafety implication: Pass')
        flag,sub = IsCoSafe(formula)
        self.assertTrue(flag)

    def test_cosafe_implication_pass(self):
        formula = ['imp',['a'],['b']]
        print('Testing cosafety implication: Pass')
        flag,sub = IsCoSafe(formula)
        self.assertTrue(flag)


    def test_cosafe_and_pass(self):
        formula = ['and',['imp',['a'],['F',['b']]],['imp',['a'],['F',['b']]],['imp',['a'],['F',['b']]],['imp',['a'],['U',['not',['a']],['b']]]]
        print('Testing cosafety and/or: Pass')
        flag,sub = IsCoSafe(formula)
        self.assertTrue(flag)

    def test_cosafe_and_fail_bad_subformula(self):
        formula = ['and',['imp',['a'],['F',['b']]],['imp',['F',['a']],['F',['b']]],['imp',['a'],['F',['b']]],['imp',['a'],['U',['not',['a']],['b']]]]
        print('Testing cosafety and/or: Fail 1')
        flag,sub = IsCoSafe(formula)
        self.assertFalse(flag)
        self.assertEqual(sub, ['F',['a']])

    def test_mix_formula(self):
        formula = ['and',['G',['a']],['imp',['F',['a']],['F',['b']]],['imp',['a'],['F',['b']]],['imp',['a'],['U',['not',['a']],['b']]]]
        flag, sub = IsCoSafe(formula)
        print('Testing mixed formula')
        self.assertFalse(flag)
        self.assertEqual(['G',['a']],sub)


if __name__ == '__main__':
    unittest.main()
