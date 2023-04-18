#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from FormulaTools import *
import spot

SpecialSyntax = {}
SpecialSyntax['operators'] = ['true', 'false', 'not','and','or','imp','X','F','G','U']
SpecialSyntax['production'] = {}

op2symb = {}
op2symb['and'] = '&'
op2symb['or'] = '|'
op2symb['not'] = '!'
op2symb['imp'] = '->'
op2symb['X'] = 'X'
op2symb['F'] = 'F'
op2symb['G'] = 'G'
op2symb['U'] = 'U'


def puns2spot(formula):
    """
    Translates PUnS Tree format formula into a valid spot string and returns s spot formula

    Parameters
    ----------
    formula : Valid PUnS tree syntax formulas. Stacked and/ors are allowed

    Returns
    -------
    spot_formula: a spot.formula object that can be translated into any valid spot compatible syntax or automata.
    """
    spot_string = ltl_tree2string(formula)
    return spot.formula(spot_string)

def spot2puns(spot_formula):
    """
    Converts a spot formula into a list structure compatitible with the PUnS system

    Parameters
    ----------
    spot_formula : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    a=1

def ltl_string2tree(prefix_string):
    """
    Converts a prefix formula string output by spot into an equivalent PUnS list representation.

    Parameters
    ----------
    prefix_string : string output from spot.formula.__format__('l'). Note please do not manually
                    generate this string as far as possible. This function does not implement a syntax check.

    Returns
    -------
    None.

    """
    a=1
    

def ltl_tree2string(formula):
    
    """
    Translates an LTL formula in the tree format to a SPOT compatible string format.
    
    Parameters
    ----------
    formula : Input LTL formula containing only the logical operators, 'X','F','G','U'

    Returns
    -------
    string : Spot compatible LTL formula string
    """
    #print(formula)
    if not CheckSpecialSyntax(formula, SpecialSyntax)[0]:
        print('Invalid Formula, Check LTL syntax. Note this translator only supports, X, F, G, U temporal operators')
        return ''
    literals = set(['true','false',True, False])
    special_ops = set(['and','or'])
    binary_ops = set(['U','imp'])
    unary_ops = set(['X','F','not','G'])
    
    # We know that the formula is valid syntax
    
    if IsAtom(formula[0]):
        return formula[0]
    
    elif formula[0] in literals:
        return '1' if formula[0] in ['true' or True] else '0'
    
    elif formula[0] in special_ops:
        op = op2symb[formula[0]]
        ltl_string = ltl_tree2string(formula[1])
        for subformula in formula[2::]:
            ltl_string =  ltl_string + f' {op} '  + ltl_tree2string(subformula)
        ltl_string = '(' + ltl_string + ')'
        return ltl_string
    
    elif formula[0] in binary_ops:
        op = op2symb[formula[0]]
        return '(' + ltl_tree2string(formula[1]) + ')' + f' {op} ' + '(' + ltl_tree2string(formula[2]) +')'
    
    elif formula[0] in unary_ops:
        op = op2symb[formula[0]]
        return '(' + f' {op} ' + ltl_tree2string(formula[1]) + ')' 

    

if __name__ == '__main__':
    
    formula2 = ['and',['a'],['b'],['c']]
    
   