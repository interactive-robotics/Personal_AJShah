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

prefix2puns_opmap = {}
prefix2puns_opmap['&'] = 'and'
prefix2puns_opmap['|'] = 'or'
prefix2puns_opmap['i'] = 'imp'
prefix2puns_opmap['!'] = 'not'
prefix2puns_opmap['U'] = 'U'
prefix2puns_opmap['X'] = 'X'
prefix2puns_opmap['F'] = 'F'
prefix2puns_opmap['G'] = 'G'

def simplify_puns(formula):
    """
    Simplifies an input PUnS formula into an rewritten PUnS formula

    Parameters
    ----------
    formula : A valid PUns formula

    Returns
    -------
    simplified_formula : A valid PUnS formula

    """
    spot_formula = puns2spot(formula)
    spot_formula = spot.simplify(formula)
    return spot2puns(spot_formula)


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
    spot_string = _ltl_tree2string(formula)
    return spot.formula(spot_string)

def spot2puns(spot_formula:spot.formula):
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
    spot_formula = spot.unabbreviate(spot_formula,'RMW^e')
    prefix_string = spot_formula.__format__('l')
    return _ltl_string2tree(prefix_string)

def _ltl_string2tree(prefix_string):
    """
    Converts a prefix formula string output by spot into an equivalent PUnS list representation.

    Parameters
    ----------
    prefix_string : string output from spot.formula.__format__('l'). Note please do not manually
                    generate this string as far as possible. This function does not implement a syntax check.

    Returns
    -------
    formula : list. Encodes the formula in PUnS valid format
    
    continuation : list of remaining non-inserted propositions after the formula has been returned

    """
    literals = set(['t','f'])
    binary_operators = set(['&','|','i','U','R'])
    unary_operators = set(['X','F','G','!'])
    
    elements = prefix_string.replace('\"','').split(' ')
    #formula = []
    
    def parse_elements(elements):
        if len(elements) == 0:
            return None
        elif elements[0] not in literals | binary_operators | unary_operators:
            return [elements[0]], elements[1:]
        elif elements[0] in literals:
            return (['true'], elements[1:]) if elements[0] == 't' else (['false'], elements[1:])
        elif elements[0] in unary_operators:
            f, continuation = parse_elements(elements[1:])
            return ([prefix2puns_opmap[elements[0]], f], continuation)
        elif elements[0] in binary_operators:
            f1, continuation = parse_elements(elements[1:])
            f2, continuation = parse_elements(continuation)
            return ([prefix2puns_opmap[elements[0]], f1, f2],continuation)
    return parse_elements(elements)[0]
    

def _ltl_tree2string(formula):
    
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
    
    a=1
    
   