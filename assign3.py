# -*- coding: utf-8 -*-
"""
Created on Sun May 20 12:45:38 2018

@author: chant
"""
#x is bottles you sell 

#x<s[j] #the bottles you sell must be less than what you have 

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

#State is how many bottles you have 
#def Sale(x,j) :
 ##  return Profit 

def F(a, t): 
    if a <= 15: 
        return 1.5*a+10 
    else: 
        a == 0
        
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
                

##CONSTRAINTS 
#a <= 15 
#s <= 10 

