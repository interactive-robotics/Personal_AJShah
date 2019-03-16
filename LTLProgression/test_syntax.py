#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 17:06:52 2019

@author: ajshah
"""

import unittest
from FormulaTools import *

class TestSyntax(unittest.TestCase):
    
    def test_Vocab(self):
        Vocabulary = set(['a','b','c'])
        formula = ['and',['F',['not',['a']]],['or',['a'],['c']],['U',['F',['a']],['b']]]
        ReturnedVocab = GetVocabulary(formula, set())
        print('Testing Vocabulary extraction')
        self.assertEqual(Vocabulary, ReturnedVocab)
        

    def test_IsAtom(self):
        formula = ['not',['a']]
        print('Testing  Is Atom: Test 1')
        self.assertFalse(IsAtom(formula[0]))
    
    def test_IsAtom2(self):
        formula = ['a']
        print('Testing is atom: Test 2')
        self.assertTrue(IsAtom(formula[0]))
    
    def test_SyntaxVerification_atom(self):
        formula = ['a','a']
        print('Testing syntax verification single atom: fail')
        (flag, subformula) = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, ['a','a'])
    
    def test_VerifySyntax_IsList(self):
        formula = 'a'
        print('Testing list checking in formula')
        (flag, subformula) = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, 'a')
        
        
    def test_SyntaxVerification_atom2(self):
        formula = ['a']
        print('Testing syntax verification single atom: pass')
        self.assertTrue(VerifyFormulaSyntax(formula)[0])
    
    def test_SyntaxVerification_unary(self):
        formula = ['F',['a']]
        print('Testing Syntax verification unary operator parity: Pass')
        (flag, subformula) = VerifyFormulaSyntax(formula)
        self.assertTrue(flag)
        self.assertEqual(subformula,'Unary')
        
    def test_SyntaxVerification_unary2(self):
        formula = ['F',['a'], ['a']]
        print('Testing Syntax verification unary operator parity: fail 1')
        (flag, subformula) = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, ['F',['a'],['a']])
        
    def test_SyntaxVerification_unaryPass(self):
        formula = ['not',['not',['a']]]
        print('Testing Syntax verification Unary operator subformula: pass')
        (flag, subformula) = VerifyFormulaSyntax(formula)
        self.assertTrue(flag)
        self.assertEqual(subformula,'Unary')
        
    def test_SyntaxVerification_unaryfail(self):
        formula = ['not', 'a']
        print('Testing Syntax verification Unary operator subformula: fail')
        (flag,subformula) = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula,'a')
    
    def test_SyntaxVerification_AndOr(self):
        formula = ['and',['a'],['b'],['F',['c']]]
        print('Testing Syntax verification for And and Or: pass')
        flag,subformula = VerifyFormulaSyntax(formula)
        self.assertTrue(flag)
        self.assertEqual(subformula,'AndOr')
    
    def test_SyntaxVerification_AndOr2(self):
        formula = ['and',['a']]
        print('Testing Syntax verification AndOr parity: Fail')
        flag,subformula = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, ['and',['a']])
        
    def test_SyntaxVerification_AndOr3(self):
        formula = ['and','a',['a'],['a']]
        print('Testing syntax verification, AndOr subformula: Fail')
        flag, subformula = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, 'a')
        
    def test_SyntaxVerification_BinaryPass(self):
        formula = ['imp',['a'],['a']]
        print('Testing syntax verification binary operators parity: Pass')
        flag, subformula = VerifyFormulaSyntax(formula)
        self.assertTrue(flag)
        self.assertEqual(subformula, 'Binary')
        
    def test_SyntaxVerification_BinaryParity(self):
        formula = ['imp',['a'],['a'],['a']]
        print('Testing syntax verification binary parity check: Fail')
        flag,subformula = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, ['imp',['a'],['a'],['a']])
        
        formula = ['imp',['a']]
        flag,subformula = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, ['imp',['a']])
        
    
    def test_SyntaxVerification_Binary_subformulaFail(self):
        formula = ['imp',['not'],'a']
        flag,subformula = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula,['not'])
        
    
    def test_Complex_Pass(self):
        formula = ['and',['G',['a']], ['imp', ['p'], ['F',['a']]], ['imp', ['p'], ['F',['a']]], ['imp',['p'], ['U',['not',['a']],['b']]]]
        print('Testing Complex formula: Test 1')
        flag, subformula = VerifyFormulaSyntax(formula)
        self.assertTrue(flag)
        
    
    def test_Complex_Fail1(self):
        formula = ['and',['G',['a']], ['imp', ['p'], ['F',['a']]], ['imp', ['p'], ['F']], ['imp',['p'], ['U',['not',['a']],['b']]]]
        print('Testing Complex formula: Test 2')
        flag, subformula = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula,['F'])
        
    
    def test_Complex_Fail2(self):
        formula = ['and',['G',['a']], ['imp', ['p'], ['F',['a']]], ['imp', 'p', ['F',['a']]], ['imp',['p'], ['U',['not',['a']],['b']]]]
        print('Testing Complex formula: Test 3')
        flag, subformula = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, 'p')
        
    def test_Complex_Fail3(self):
        formula = ['and',['G',['a']], ['imp', ['p'], ['F',['a']]], ['imp', ['p'], ['F',['a']],[]], ['imp',['p'], ['U',['not',['a']],['b']]]]
        print('Testing Complex formula: Test 4')
        flag, subformula = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, ['imp', ['p'], ['F',['a']],[]])
    
    def test_Complex_Fail4(self):
        formula = ['and',['G',['a']], ['imp', ['p'], ['F',['a']]], ['imp', ['p'], ['F',['a']]], ['imp',['p'], ['U',['not',['a']],'b']]]
        print('Testing Complex formula: Test 5')
        flag, subformula = VerifyFormulaSyntax(formula)
        self.assertFalse(flag)
        self.assertEqual(subformula, 'b')
    
if __name__=='__main__':
    unittest.main()