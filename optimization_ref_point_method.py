# -*- coding: utf-8 -*-

import ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize

"""
Created on Thu Apr 30 16:27:05 2020

@author: Antti Luopajärvi

"""

global data
data = pd.read_csv('data/final_data.csv',index_col=0)
objectives = ['Expected return', 
              'Sustainability',
              'Dividend yield',
              'Clean energy use',
              'P/E ratio']

def f(x):
    """
    Multiobjective portfolio optimization problem.

    Parameters
    ----------
    x : list
        decision variables.

    Returns
    -------
        objective function values.
    
    Examples
    --------
        x = [0.1,0.2,0,...,0.7]
        f(x) === [0.09141117215909475, 0.347, 0.953, 0.2, 36.8958284]
        x = [0,0,...,0]
        f(x) === [0.0, 0.0, 0.0, 0.0, 0.0]
        x = [0,0.2,0,0.8,...,0.1]
        f(x) === "invalid values of x, sum of weights over 1."

    """
    
    indeces = [i for i in range(len(x))]
    values = []
    for v in range(4): # first four objectives to maximize
        values.append(sum([x_i*company_values(i)[v] for x_i,i in zip(x,indeces)]))
    values.append(sum([x_i*company_values(i)[4] for x_i,i in zip(x,indeces)]))
    return values


def beta(company_i):
    """
    Return Sharpe's beta for given company.

    Parameters
    ----------
    company_i : int
        index of company.

    Returns
    -------
    beta.
    
    Examples
    --------
    beta(1)   ===  0.880157
    beta(-4)  ===  1.092401
    beta(450) ===  "Invalid company index."

    """
    
    try:
        return data.iloc[company_i]['Beta']
    except IndexError:
        print("Invalid company index.")
        return

    
def company_values(company_i):
    """
    Returns values from data for given company.

    Parameters
    ----------
    company_i : int
        index of company.

    Returns
    -------
    values : list
        list including :return, sustainability, dividend yield, clean energy use, p/e-ratio.
        
    Examples
    --------
        company_values(1)   === [0.0955335823027451, 0.85, 1.05, 0.0, 29.787233]
        company_values(202) === [0.1465890818624118, 0.53, 3.63, 0.0, 12.361261]
        company_values(555) === 'Index out of bounds for company'
                                    array([0., 0., 0., 0., 0.])

    """
    
    if company_i > len(data):
        print('index out of bounds for company')
        return np.zeros(5)
    
    company = data.iloc[company_i]
    return [company['Expected return'], company['ESG score'], company['Dividend yield'], \
           sum([company['Clean200'],company['ScienceBasedTargets']]),company['P/E']]

        
def calculate_ideal(f,x,b_tol):
    """
    Function for calculating the ideal vector for multiobjective problem f.
    
    Args:
        f(list): Objective functions
        x(list): Starting point
        b_tol(float) : Tolerance for beta constraint.
        
    Returns:
        ideal,value(np.array,float): Ideal vector and values of f at the ideal point.
    """
    
    # initialize for five objectives
    ideal = [0]*5
    # bounds for decision variables
    b = [(0,1)]*len(x)
    # constraint
    betas = np.array([beta(c) for c in range(len(x))])
    t = b_tol # tolerance for beta constraint
    c = (
         # sum of weights = 1
         {'type':'eq','fun':lambda x: 1-sum(x)}, 
         
         # sum of beta = 1
         # transforming a strict equality constraint into two inequality constraints, 
         # to relax the constraint.
         {'type':'ineq','fun': lambda x: 1+t-sum(np.array(x)*betas)}, 
         {'type':'ineq','fun': lambda x: sum(np.array(x)*betas)-1+t}
        )

    #list for storing the actual solutions, which give the ideal
    solutions = [] 
    starting_point = x
    
    # maximize the first four objectives
    for i in range(4):
        res=minimize(
            # maximize each objective at the time
            lambda x: -f(x)[i], starting_point, method='SLSQP'
            # use of Jacobian resulted in worse results
            #,jac=ad.gh(lambda x: f(x)[i])[0]
            ,options = {'disp':False, 'ftol': 1e-20, 'maxiter': 1000}
            ,bounds = b
            ,constraints = c)
        solutions.append(f(res.x))
        ideal[i]=res.fun
    
    # switch the signs 
    ideal = [x*-1 for x in ideal]
    
    # minimize the fifth objective, p/e ratio
    res=minimize(
        lambda x: f(x)[4], starting_point, method='SLSQP'
        #Jacobian using automatic differentiation
        #,jac=ad.gh(lambda x: f(x)[i])[0]
        ,options = {'disp':False, 'ftol': 1e-20, 'maxiter': 1000}
        ,bounds = b
        ,constraints = c)
    solutions.append(f(res.x))
    ideal[4]=res.fun
           
    return ideal,solutions


def f_normalized(x,i,n):
    """
    Returns the values of normalized objective functions at point x.
    
    Args:
        x(np.array): Values of x.
        i(list): ideal vector
        z(list): nadir vector
        
    Returns:
        (float): Values of objective functions.
    """
    
    z = f(x)
    return [(zi-zideali)/(znadiri-zideali) for 
            (zi,zideali,znadiri) in zip(z,i,n)]


def asf(f,ref,b_tol,x_start,z_ideal,z_nadir,rho):
    """
    Implementation of achievement scalarizing function.

    Parameters
    ----------
    f : function
        objective functions.
    ref : list
        reference point.
    b_tol : float
        tolerance for beta constraint.
    x_start : list
        starting point.
    z_ideal : list
        ideal vector.
    z_nadir : list
        nadir vector.
    rho : float
        augmentation parameter.

    Returns
    -------
    scipy.optimize.optimize.OptimizeResult
        result of optimization.
    
    Examples
    --------

    """
    
    # bounds and constraints
    b = [(0,1)]*len(x_start)
    betas = [beta(c) for c in range(len(x_start))]
    t = b_tol # tolerance for beta constraint
    
    c = (
         # sum of weights = 1
         {'type':'eq','fun':lambda x: 1-sum(x)}, 
         
         # sum of beta = 1
         # transforming a strict equality constraint into two inequality constraints, 
         # to relax the constraint.
         {'type':'ineq','fun': lambda x: 1+t-sum(np.array(x)*betas)}, 
         {'type':'ineq','fun': lambda x: sum(np.array(x)*betas)-1+t}
        )
    
    # normalizing the reference point
    ref_norm = [(refi-z_ideali)/(z_nadiri-z_ideali) 
                for (refi,z_ideali,z_nadiri) in zip(ref,z_ideal,z_nadir)]
    
    # scalarized function
    def obj(x):
        return np.max(np.array(f(x,z_ideal,z_nadir))-ref_norm)\
           +rho*np.sum(f(x,z_ideal,z_nadir))
    
    start = x_start
    res=minimize(
        #Objective function defined above
        obj, 
        start, method='SLSQP'
        #Jacobian using automatic differentiation
        ,jac=ad.gh(obj)[0]
        #bounds given above
        ,bounds = b
        ,constraints = c
        ,options = {'disp':True, 'ftol': 1e-20,
                'maxiter': 1000})
    return res


def solve_problem(f,x_start,ref,b_tol):
    """
    Solve the multiobjective portfolio problem.

    Parameters
    ----------
    f : function
        objective functions
    x_start : list
        starting values for decision variables.
    ref : list
        reference point provided by decision maker.
    b_tol : float
        tolerance for beta constraint.

    Returns
    -------
    scipy.optimize.optimize.OptimizeResult
        result of optimization.

    """
    
    # 1. calculation of ideal and nadir vectors    
    z_ideal, solutions= calculate_ideal(f,x_start,b_tol)
    print ("Ideal vector:\n"+str(z_ideal))
    
    print("\n === Estimation of Nadir vector === ")
    # Estimation of Nadir vector from payoff table:
    print("\nPayoff-table:")
    for s in solutions:
        print(s)
    
    print("\nNadir vector is put together from each of the objective function's \"worst\" \
          value in the table")
    
    # minimums of first four objectives    
    z_nadir = [min(np.transpose(solutions)[s]) for s in range(len(solutions)-1)]           
    
    # maximum of last objective
    z_nadir.append(max(np.transpose(solutions)[-1]))
    print("Nadir vector:\n",z_nadir)
    
    # 2. normalizing the objective functions
    print("\nAfter normalizing the objective functions using ideal- and nadir-vectors:")
    print("normalized value for the problem at " + str(x0) + " is")
    print(f_normalized(x0,z_ideal,z_nadir))
    
    # 3. solving the problem   
    print("\n=== SOLUTION ===")
    rho = 0.000001
    res = asf(f_normalized,ref,tol,x0,z_ideal,z_nadir,rho)
    print("Proportional amounts to invest in companies are:\n")
    for c in range(len(x0)):
        print(data['Company'].values[c] + " : " + str(res.x[c]))
        
    print("\nObjective function values are:\n")
    for i in range(len(objectives)):
        print(objectives[i] + " : " + str(f(res.x)[i]))
    print("Portfolio beta : ",sum(res.x[i]*beta(i) for i in range(len(res.x))))
    print("Ideal vector: " +str(z_ideal))
    print("Sum of weights : ",sum(res.x))
    if sum(res.x) < 1+0.000000001:
        print("Solution is feasable")
    else : print("Solution is infeasable")
    
    return res
    

n = 30
x0 = [1/n]*n # start with equal weights
ref = [0.1,0.5,3,1,15]
tol = 0.1 # tolerance for beta constraint
solve_problem(f,x0,ref,tol)