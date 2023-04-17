#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import spot

def expand_and_or(formula):
    
    if len(formula) == 1: # Its a proposition 
        return formula
    elif formula[0] in ['and','or']: # Need to create the binary and/or stack
        if len(formula) <= 3:
            return formula
        else:
            a = [formula[0]]
            return [formula[0], expand_and_or(a + formula[2:]), formula[1]]
    elif formula[0] in ['F','G','X','not']: # Unary operator, No change to the formula, but will have to collapse the subformulas if required
        return [formula[0], expand_and_or(formula[1])]
    else: #non and/or binary operator
        return [formula[0], expand_and_or(formula[1]), expand_and_or(formula[2])]

def list_to_spot(formula):
    """
    Convert nested list format of LTL formulas used by PUnS to the string format used by SPOT.

    Parameters
    ----------
    formula : input LTL formula as valid puns package Obligations formula

    Returns
    -------
    spot_formula : string in prefix spot format

    """
    
    formula = expand_and_or(formula) # expand the shorthand available to 'and' and 'or' operators
    
    #replace operators with spot operators
    formula_string = str(formula)
    formula_string = formula_string.replace('[','').replace(']','').replace(',','') #remove punctuations and parenthesis, and we already have a valid prefix formula
    formula_string = formula_string.replace('\'and\'','&').replace('\'or\'','|').replace('not','!').replace('\'imp\'','i') #Replace logical operators first
    formula_string = formula_string.replace('\'F\'', 'F').replace('\'G\'','G').replace('\'X\'','X').replace('\'U\'','U') # Replace all temporal operators
    formula_string = formula_string.replace('\'true\'','t').replace('True','t').replace('\'false\'','f').replace('False','f') #Replace literals
    formula_string = formula_string.replace('\'','\"') #replace quotations around propositions with required spot format
    return formula_string
    

if __name__ == '__main__':
    
    formula2 = ['and',['a'],['b'],['c']]
    
    expand_and_or(formula2)