# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 16:13:12 2022

@author: AJShah
"""

from puns.FormulaTools import *

SpecialSyntax = {}
SpecialSyntax['operators'] = ['not','and','or','imp','X','F','G','U']
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

# We only support these operators for translation from LTLf to SPOT compatible LTL formula


def ltl_tree2string(formula):
    
    """
    Translates an LTL formula in the tree format to a SPOT compatible string format.
    
    Parameters
    ----------
    formula : Input LTL formula containing only the logical operators, 'X','F','G','U'

    Returns
    -------
    string
    Spot compatible LTL formula string
    """
    
    if not CheckSpecialSyntax(formula, SpecialSyntax)[0]:
        print('Invalid Formula, Check LTL syntax. Note this translator only supports, X, F, G, U temporal operators')
        return ''
    
    special_ops = set(['and','or'])
    binary_ops = set(['U','imp'])
    unary_ops = set(['X','F','not','G'])
    
    # We know that the formula is valid syntax
    
    if IsAtom(formula[0]):
        return formula[0]
    
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

def ltlf2ltl(formula):
    """
    Translates LTLf formula input in the tree format to a SPOT compatibile LTL formula in the tree format

    Parameters
    ----------
    formula : Input LTLf formula containing only the logical operators, 'X','F','G','U'

    Returns
    -------
    Spot compatible LTL formula that includes an additional proposition 'live'

    """
    base_ltl = _ltlf2ltl(formula)
    append_ltl = ['G',['U', ['live'], ['not',['live']]]]
    
    if base_ltl[0] == 'and':
        base_ltl.append(append_ltl)
        ret_ltl = base_ltl
    else:
        ret_ltl = ['and',base_ltl, append_ltl]
    
    return ret_ltl

def _ltlf2ltl(formula):
    """
    Recursive helper formula for the translation

    Parameters
    ----------
    formula : list
        Input LTLf formula containing only logical operators and 'X','F','G','U'

    Returns
    -------
    list
        LTL formula in the tree syntax containing necessary transforms of the subformulas.

    """
    if IsAtom(formula[0]):
        return formula
    
    elif formula[0] in ['and','or']:
        retformula = ['and']
        for subformula in formula[1::]:
            retformula.append(_ltlf2ltl(subformula))
        return retformula
    
    elif formula[0] == 'imp':
        return ['imp',_ltlf2ltl(formula[1]),_ltlf2ltl(formula[2])]
    
    elif formula[0] == 'not':
        return ['not', _ltlf2ltl(formula[1])]
    
    elif formula[0] == 'X':
        return ['X',['and',[_ltlf2ltl(formula[1])],['live']]]
    
    elif formula[0] == 'G':
        return ['G',['or',_ltlf2ltl(formula[1]),['not',['live']]]]
    
    elif formula[0] == 'F':
        return ['F',['and',_ltlf2ltl(formula[1]),['live']]]
    
    elif formula[0] == 'U':
        return ['U',formula[1],['and', _ltlf2ltl(formula[2]),['live']]]
            