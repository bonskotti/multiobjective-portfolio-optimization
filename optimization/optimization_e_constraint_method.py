# -*- coding: utf-8 -*-

import ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyomo.environ import *
from pyomo.opt import SolverFactory
from scipy.optimize import minimize

"""
Created on Thu Apr 30 16:27:05 2020

@author: Antti Luopajärvi

"""

def params(data):
    """
    Initialize optimization problem by gathering parameter data together.

    Parameters
    ----------
    data : dataframe
        problem data.

    Returns
    -------
    params : list
        parameter data for problem.

    """
    
    names = data['Company'].values
    
    # parameters
    companies = data['Company'].index
    betas = data['Beta'].values
    returns = data['Expected return'].values
    sustainabilities = data['ESG score'].values
    cleans = data['Clean200']+data['ScienceBasedTargets']
    dys = data['Dividend yield'].values
    pes = data['P/E'].values
    params = [companies,betas,returns,sustainabilities,dys,cleans,pes]
    return names, params


def rule(model, params):
    """
    Returns an expression of constraint/objective rule. Used in creating constraints and
    objectives for optimization problem with Pyomo.

    Parameters
    ----------
    model : pyomo.core.base.PyomoModel.ConcreteModel
        pyomo optimization model.
    params : list
        parameter values.

    Returns
    -------
    expression of constaint/optimization rule.

    """
    
    return sum(model.x[i]*params[i] for i in range(len(data)))


def solve_problem(params,
                  names,
                  objectives,
                  obj_i,
                  constraints,
                  b_tol):
    """
    Solve the problem using epsilon constraint method with Pyomo.

    Parameters
    ----------
    params : list
        parameter data for problem.
    names : list
        company names for printing output.
    objectives : list
        list of objectives:
        
        ['Expected return',
         'Sustainability',
         'Dividend yield',
         'Clean energy use',
         'P/E ratio']
        
    obj_i : int
        index of objective in list of objectives.
    constraints : list
        lower/upper bounds for constraint functions.
    b_tol : float
        tolerance for beta constraint.

    Returns
    -------
    None.

    """
    
    model = ConcreteModel()
    # decision variables
    default = 1/len(params[0]) # initialize with equal weights
    model.x = Var(params[0], initialize=default, bounds=(0,0.05), within=NonNegativeReals)
       
    # objective function
    if obj_i < 4:
        model.obj =  Objective(expr=rule(model,params[obj_i+2]),sense=maximize)
    else:
        # p/e ratio minimized
        model.obj =  Objective(expr=rule(model,params[obj_i+2]))
    
    # constraints
    # delete objective function from params
    del params[obj_i+2]
    # beta
    model.beta_geq = Constraint(expr = rule(model,params[1]) <=1+b_tol)
    model.beta_leq = Constraint(expr = rule(model,params[1]) >=1-b_tol)
    model.c1 = Constraint(expr = rule(model,params[0]+2) >= constraints[0])
    model.c2 = Constraint(expr = rule(model,params[1]+2) >= constraints[1])
    model.c3 = Constraint(expr = rule(model,params[2]+2) >= constraints[2])
    if obj_i < 4:
        model.c4 = Constraint(expr = rule(model,params[3]+2) <= constraints[3])
    else:
        # p/e ratio is as objective function
        model.c4 = Constraint(expr = rule(model,params[3]+2) >= constraints[3])
    
    """
    # sustainability
    model.sustainability = Constraint(expr = rule(model,sustainabilities) >= 0.4)
    # clean energy use
    model.clean = Constraint(expr = rule(model,cleans) >= 1)
    # dividend yield
    model.dy = Constraint(expr = rule(model,dys) >= 5)
    # p/e ratio
    model.pe = Constraint(expr = rule(model,pes) <= 20)
    """
    # sum of weights
    model.sum_weights = Constraint(expr = rule(model,np.ones(len(data))) == 1)
    
    # solve
    opt = SolverFactory('glpk')
    res = opt.solve(model, tee=True)
    
    print("\nObjective function value")
    
    print("\nBeta")
    print(sum(model.x[i].value*params[1][i] for i in range(len(params[0]))))
    
    print("\nCompanies to invest in:")
    c = []
    w = []
    for j in range(len(model.x)):
        if model.x[j].value != 0:
            c.append(names[j])
            w.append(model.x[j].value)
            print(names[j] + str(model.x[j].value))
    

data = pd.read_csv('../data/version_13.csv')
n,p = params(data)
objectives = ['Expected return',
         'Sustainability',
         'Dividend yield',
         'Clean energy use',
         'P/E ratio']
obj_i = 4
constraints = [9,0.6,2,1]
b_tol = 0.1
solve_problem(p,n,objectives,obj_i,constraints,b_tol)