# Multiobjective portfolio optimization

![Alt text](img/sm_crop.jpg?raw=true "Title")

In this repository, multiobjective portfolio optimization is performed using two different optimization methods. In addition to traditional financial objectives, the optimization methods take in consideration environmental, social, and governance sustainability of portfolio.

----
## Problem description

Portfolio optimization traditionally aims to select assets that bring the most return on investment with the least risk. However, for some investors, there are also other factors to consider in addition to direct financial gain. Technology has made stock investing more easily approachable than ever, and growing number of new investors search not only to get return on their money but also to invest in companies with sustainable business. The term ESG-investing means buying in companies with their environmental, social, and governance strategies in consideration.

## Quick start

1. Clone this repository using `git clone https://github.com/bonskotti/multiobjective-portfolio-optimization.git`

2. Install requirements using `pip install -r requirements.txt`. In addition, you should have [Glpk](https://www.gnu.org/software/glpk/) installed. Easy way to do so is with conda: `conda install glpk`.

3. Run either [optimization_e_constraint_method.py](../blob/master/optimization_e_constraint_method.py) or [optimization_ref_point_method.py](../blob/master/optimization_ref_point_method.py) to solve the problem.

### Example usage - e-constraint method

```
data = pd.read_csv('data/final_data.csv') # load data
n,p = params(data) # organize parameters and get names of companies
obj_i = 4 # select objective to be optimized

# set constraints
constraints = [
                0.09 # return
               ,0.6 # sustainability
               ,2   # dividend yield
               ,1   # clean energy use
               #,15 # p/e ratio
               ]
               
b_tol = 0.1 # tolerance for beta
solve_problem(p,n,obj_i,constraints,b_tol)
```
### Example usage - Reference point method

```
n = 30 # number of companies
x0 = [1/n]*n # start with equal weights
ref = [0.1,0.5,3,1,15] # aspiration levels for objectives
tol = 0.1 # tolerance for beta constraint
solve_problem(f,x0,ref,tol)
```
**Note**: Calculation of ideal and nadir vectors is computationally expensive - if you are in a hurry, decrease the number of companies (n) when solving with reference point method.

----

## Data

**ESG-related data** is from three sources:

1. Robecosam ranks companies by ESG-scores, from 0 to 100. https://yearbook.robecosam.com/ranking/

2. Clean200 ranks companies by their solutions for transition to clean energy future. No scores, company either is on the list or not. https://www.asyousow.org/report-page/2020-clean200

3.  ScienceBasedTargets ranks companies by their science-based climate actions. No scores, company either is on the list or not. https://sciencebasedtargets.org/companies-taking-action/

**Financial data** is from two sources:

1. Yahoo Finance

2. Nasdaq

After preprocessing, final dataset consists of 361 companies, listed in NYSE, NASDAQ, OMXCO, OMXHE, and OMXST.

## Modeling

For objectives, following are used:

1. Maximize expected return.
2. Maximize environmental, social, and corporate- sustainability.
3. Maximize dividend yield.
4. Maximize clean energy use.
5. Minimize price-earnings ratio.
6. Optimize portfolio volatility.

*In this problem, portfolio volatility is optimized using Sharpe's beta. Portfolio is set to be as volatile as whole market in average, so beta is aimed to be equal to 1.*

For **decision variables**, proportional amount (weight) to invest in company i is used.

For **constraints**, 

1. Sum of weights should be equal to one.
2. Weight of a single asset should be between 0 and 1.

## Optimization

Optimization is performed using two methods,

1. Epsilon-constraint method.
2. Reference point method.

## Results

**1. Epsilon constraint method**

Some of the Pareto optimal solutions obtained:

![Alt text](img/e_constraint_3.png?raw=true "Title")


![Alt text](img/e_constraint_4.png?raw=true "Title")

**2. Reference point method**

![Alt text](img/ref_point_2.png?raw=true "Title")

## Interactive solver

Both of the optimization methods can be used interactively with the decision maker. To demonstrate this, a simple CLI-based solver application is under development. At the moment, the solver supports epsilon-constraint method. 

### Usage

Simply run [optimization_e_constraint_method.py](../blob/master/optimization_e_constraint_method.py)
