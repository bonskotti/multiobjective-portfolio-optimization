# Multiobjective portfolio optimization

In this repository, multiobjective portfolio optimization is performed using two different optimization methods. In addition to traditional financial objectives, the optimization methods take in consideration environmental, social, and governance sustainability of portfolio.

### Problem description

Portfolio optimization traditionally aims to select assets that bring the most return on investment with the least risk. However, for some investors, there are also other factors to consider in addition to direct financial gain. Technology has made stock investing more easily approachable than ever, and growing number of new investors search not only to get return on their money but also to invest in companies with sustainable business. The term ESG-investing means buying in companies with their environmental, social, and governance strategies in consideration.

### Data

**ESG-related data** is from three sources:

1. Robecosam ranks companies by ESG-scores, from 0 to 100. https://yearbook.robecosam.com/ranking/

2. Clean200 ranks companies by their solutions for transition to clean energy future. No scores, company either is on the list or not. https://www.asyousow.org/report-page/2020-clean200

3.  ScienceBasedTargets ranks companies by their science-based climate actions. No scores, company either is on the list or not. https://sciencebasedtargets.org/companies-taking-action/

**Financial data** is from two sources:

1. Yahoo Finance

2. Nasdaq

### Modeling

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

### Optimization

Optimization is performed using two methods,

1. Epsilon-constraint method.
2. Reference point method.

# to be continued>

