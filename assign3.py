# -*- coding: utf-8 -*-
"""
Created on Sun May 20 12:45:38 2018

@author: chant
"""



Demand = [
        6, 
        11, 
        11, 
        5, 
        6,
        5,
        10]
Days = len(Demand)

# Stage is day j in Days 

#State is how many bottles you have, s on day j 

#F(a, t) returns the cost of taking action a (i.e. ordering a bottles for the following day)
def F(a, t): 
    if a <= 15: 
        return 1.5*a+10 
    else: 
        a == 0
#C is the profit function, it assumes that the demand is sold. 
        
def C(t,s,a): 
    if s<= 10: 
        if t == 0: 
            return 0 
        else: 
            return 5*Demand[t] -F(a,t) 
    else: 
        return 5*Demand[t]-F(0, t) 
        

def V(t, s): 
    #while a<=15 and s<= 10: 
    if t == 7 : 
        return (0, 0)
            
    else: 
        return max(
            (C(t, s, a) + V(t+1, s+a - Demand[t])[0], s)
            for a in range(len(Demand)))
                
#Need to figure out how to fix t = 0, i.e. action should still be taken 
##CONSTRAINTS 
#a <= 15 
#s <= 10 
    

