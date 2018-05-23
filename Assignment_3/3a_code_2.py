# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:00:26 2018

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
Days = range(len(Demand))

##State is bottles at the beginnning of day j 
#Sj 

##Action is how many bottles that you buy for day j 
##Aj 
A= range(16)


def BottlesLeftover(s, a, j):
    return max(0, s+a-Demand[j])

def BottlesSold(s, a, j): 
    return s - BottlesLeftover(s, a, j) 

def CostDel(s, a, j): 
    if 0<a<15: 
        return 1.5*s + 10
    else: 
        return 0

def V(s,j):
    max((
                (5*BottlesSold(s, a, j)-CostDel(s, a, j) + V(j+1, s+a - Demand[j])[0]), s) for a in A)
    

#Need to add constraint that s<= 10 
#Need to add s[0] = 0