#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 11:44:14 2023

@author: ajshah
"""

from spot_wrapper import *
import unittest

test_formulas = ['Fa','Gb','Xc','x U y','a & b', 'a | b','a -> b', 'a -> (!b U c)', 'F(a & F(b & F(c & Fd)))', 'F(a R b)', 'a M b', 'a W b']

class TestSpotWrapper(unittest.TestCase):
    
    def test_syntax_consistency(self):
        for test_formula in test_formulas:
            print(f'Testing PUNS syntax consistency for {test_formula}')
            test_formula = spot.formula(test_formula)
            puns_formula = spot2puns(test_formula) # This should automatically unabbreviate
            self.assertTrue(VerifyFormulaSyntax(puns_formula)[0], msg=f'Failed Syntax check on formula {test_formula}')
    
    def test_semantic_consistency(self):
        for test_formula in test_formulas:
            print(f'Testing semantics consistency for {test_formula}')
            test_formula = spot.formula(test_formula)
            puns_formula = spot2puns(test_formula)
            translated_formula = puns2spot(puns_formula)
            self.assertTrue(spot.are_equivalent(test_formula, translated_formula), msg = f'Failed Semantics consistency check {str(test_formula)}')
                                
    

if __name__ == '__main__':
    unittest.main()
    