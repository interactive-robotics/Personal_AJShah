#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 17:43:13 2019

@author: ajshah
"""

import unittest
from puns.Progression import *

class TestProgression(unittest.TestCase):

    def test_SingleProgression_G1(self):
        formula = ['G',['P']]
        TraceSlice = {}
        TraceSlice['P'] = False
        formula = ProgressSingleTimeStep(formula, TraceSlice)
        print('Testing single time step progression for G: Test 1')
        self.assertEqual(formula, [False])

    def test_SingleProgression_G2(self):
        formula = ['G',['P']]
        TraceSlice = {}
        TraceSlice['P'] = True
        formula1 = ProgressSingleTimeStep(formula, TraceSlice)
        print('Testing single time step progression for G: Test 2')
        self.assertEqual(formula1, ['G',['P']])

    def test_SingleProgression_F1(self):
        formula = ['F',['P']]
        TraceSlice = {}
        TraceSlice['P'] = False
        formula = ProgressSingleTimeStep(formula, TraceSlice)
        print('Testing single time step progression for F: Test 1')
        self.assertEqual(formula, ['F',['P']])

    def test_SingleProgression_F2(self):
        formula = ['F',['P']]
        TraceSlice = {}
        TraceSlice['P'] = True
        formula = ProgressSingleTimeStep(formula, TraceSlice)
        print('Testing single time step progression for F: Test 2')
        self.assertEqual(formula, [True])

    def test_TraceProgression_U1(self):
        Trace = {}
        formula = ['U',['a'],['b']]
        Trace['a'] = [True, True, True, False]
        Trace['b'] = [False, True, False, False]
        Trace['length'] = 4
        formula = Progress(formula, Trace)
        print('Testing trace progression for U: Test 1')
        self.assertEqual([True], formula)

    def test_TraceProgression_U2(self):
        Trace = {}
        formula = ['U',['a'],['b']]
        Trace['a'] = [True, True, False, True, True]
        Trace['b'] = [False, False, False, True, True]
        Trace['length'] = 5
        formula = Progress(formula, Trace)
        print('Testing trace progression for U: Test 2')
        self.assertEqual(formula, [False])

    def test_TraceProgression_U3(self):
        Trace = {}
        formula = ['U',['a'],['b']]
        Trace['a'] = [True, True, True, True, False]
        Trace['b'] = [False, False, False, True, True]
        Trace['length'] = 5
        formula = Progress(formula, Trace, t=3)
        print('Testing partial trace progression for U: Test 3')
        self.assertEqual(formula, ['U',['a'],['b']])

    def test_TraceProgression_U4(self):
        Trace = {}
        formula = ['U',['a'],['b']]
        Trace['a'] = [True, True, True, True, True]
        Trace['b'] = [False, False, False, False, False]
        Trace['length'] = 5
        formula = Progress(formula, Trace)
        print('Testing trace progression for U final value')
        self.assertEqual(formula, [False])

    def test_TraceProgression_G(self):
        formula = ['and', ['G',['T0']],['G',['T1']],['G',['T2']],['G',['T3']], ['G',['T4']]]
        Signal = Constants.ImportSampleData(4)
        Signal['T1'][4] = False
        formula = Progress(formula, Signal)
        print('Testing trace progression for G: Test 1')
        self.assertEqual(formula, [False])

    def test_TraceProgression_G2(self):
        formula = ['and', ['G',['T0']],['G',['T1']],['G',['T2']],['G',['T3']], ['G',['T4']]]
        Signal = Constants.ImportSampleData(4)
        formula = Progress(formula, Signal)
        print('Testing trace progression for G: Test-2')
        self.assertEqual(formula, [True])

    def test_TraceProgression_GPartial(self):
        formula = ['and', ['G',['T0']],['G',['T1']],['G',['T2']],['G',['T3']], ['G',['T4']]]
        Signal = Constants.ImportSampleData(4)
        formula2 = Progress(formula, Signal, t=10)
        #print(formula2)
        print('Testing partial trace progression for G')
        self.assertEqual(formula, formula2)

    def test_TraceProgression_F(self):
        formula = ['and']
        for i in range(5):
            formula.append(['imp',[f'P{i}'], ['F',[f'W{i}']]])
        Signal = Constants.ImportSampleData(4)
        formula = Progress(formula, Signal)
        print('Testing trace progression for F')
        self.assertEqual(formula, [True])

    def test_TraceProgression_FPartial(self):
        formula = ['and']
        for i in range(5):
            formula.append(['imp',[f'P{i}'], ['F',[f'W{i}']]])
        Signal = Constants.ImportSampleData(4)
        formula = Progress(formula, Signal, t=Signal['length']-4)
        #print(formula)
        print('Testing partial trace progression for F')
        self.assertEqual(formula, ['F',['W3']])

    def test_TraceProgression_F_endpoint(self):
        trace = {}
        trace['P'] = [False, False, False, False, False]
        trace['length'] = 5
        formula = ['F',['P']]
        formula = Progress(formula, trace)
        print('Testing endpoint progression for F: Test 1')
        self.assertEqual(formula, [False])

    def test_TraceProgression_F_endpoint2(self):
        trace = {}
        trace['P'] = [False, False, False, False, True]
        trace['length'] = 5
        formula = ['F',['P']]
        formula = Progress(formula, trace)
        print('Testing endpoint progression for F: tTest 2')
        self.assertEqual(formula, [True])

    def test_TraceProgression_G_endpoint(self):
        trace = {}
        trace['P'] = [True, True, True]
        trace['length'] = 3
        formula = ['G',['P']]
        formula = Progress(formula, trace)
        print('Testing endpoing for G: Test 1')
        self.assertEqual(formula, [True])

    def test_TraceProgression_G_endpoint2(self):
        trace = {}
        trace['P'] = [True, True, False]
        trace['length'] = 3
        formula = ['G',['P']]
        formula = Progress(formula, trace)
        print('Testing endpoing for G: Test 2')
        self.assertEqual(formula, [False])


if __name__ == '__main__':
    unittest.main()
