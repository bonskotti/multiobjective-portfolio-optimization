# -*- coding: utf-8 -*-
"""
Created on Sat May 23 14:09:46 2020

@author: Antti Luopajärvi

Interactive multiobjective portfolio optimization. 

User can choose from two methods, 
    1) Epsilon-constraint method
    2) Reference point method (not yet implemented)
, and solve multiobjective portfolio optimization problem interactively. 

User can provide their preferences and desired levels for multiple objectives 
 ==> 1) Expected return
     2) Sustainability
     3) Dividend yield
     4) Clean energy use
     5) Price-to-earnings-ratio.

"""

from optimization_e_constraint_method import params, solve_problem
import pandas as pd


def init_data(obj_i):
    """
    Initialize data for solving the problem.

    Parameters
    ----------
    obj_i : int
        index of objective to be optimized.

    Returns
    -------
    data : DataFrame
        data for companies.
    constraints : list
        names of objectives set to constraints, according to e-constraint method.
    objective : str
        name of objective to be optimized.

    """
    data = pd.read_csv('data/final_data.csv')
    objectives = ['Expected return',
         'Sustainability',
         'Dividend yield',
         'Clean energy use',
         'P/E ratio']
    objective = objectives[obj_i]
    # drop the objective off
    objectives.remove(objective)
    constraints = objectives
    
    return data, constraints, objective


def init_problem():
    """
    Initialize multiobjective optimization problem for solving.

    Returns
    -------
    data : DataFrame
        data for companies.
    constraints : list
        names of constraint functions.
    obj_opt : str
        name of objective function.
    obj_i : int
        index of objective to be optimized.
    c : list
        bounds for constraint functions.

    """
    
    nb = int(input('Select your optimization method : \nEpsilon constraint method, press 1\
          \nReference point method, press 2 (not yet available)\n> '))
    if nb == 1:
        obj = int(input("Select an objective to be optimized:\n\
                    Expected return, press 1\n\
                    Sustainability, press 2\n\
                    Dividend yield, press 3\n\
                    Clean energy use, press 4\n\
                    P/E ratio, press 5\n>"))
        obj_i = obj-1
        data, constraints, obj_opt = init_data(obj_i)
        
        # constraints
        print("Set bounds for other objectives.")
        c1 = float(input("Bound for "+ constraints[0]+ ": "))
        c2 = float(input("Bound for "+ constraints[1]+ ": "))
        c3 = float(input("Bound for "+ constraints[2]+ ": "))
        c4 = float(input("Bound for "+ constraints[3]+ ": "))
        c = [c1,c2,c3,c4]
        
        return data,constraints,obj_opt,obj_i,c
            
    else: 
        # TO DO: Reference point method 
        print("Reference point method yet not supported.")
                

def main():
        # initialize
        data, constraints, obj_opt, obj_i, constraint_values = init_problem()
        
        # company names, parameter preprocessing
        names, par = params(data)
        
        # solve
        solve_problem(par,names,obj_i,constraint_values,0.1)
    

if __name__ == '__main__':
    main()