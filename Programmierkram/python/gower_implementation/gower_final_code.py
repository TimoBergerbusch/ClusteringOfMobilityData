"""
Custom implementation of the Gower distance in the scope of the practicle course on the topic "clustering of mobility
data" at HumTec, RWTH, SS18.

parameters:

(list) X, Y:        Data objects with variables of arbitrary types (Numerical, Categorical, [Binary]).
(list) categorical: Value at a position i is 'True', if the variable type of X[i], Y[i] are categorical, else 'False'.
(list) ranges:      Value at a position i is the value range of the variable type of X[i], Y[i]
"""

def distance (X, Y, categorical, ranges):
    # Check array sizes
    
    if (len(X) != len(Y)):
           print("Array sizes do not Match!")
           return;
    
    # Algorithm
    
    s = [0 for i in range(len(X))]
       
    for i in range(len(X)):
        if (categorical[i] == True):
            s[i] = 1 if (X[i] == Y[i]) else 0
        else:
            s[i] = 1 - abs(X[i] - Y[i]) / ranges[i]
            
    return sum(s)/len(X) 

"""
EXAMPLE

The data points have the form X, Y = (TravelDistance | Age | Gender),
whereas 'Gender' is a categorical variable, given in the 'categorical' list.
The ranges to each variable type are saved in the 'ranges' list.
"""

"""
X = [87, 40, "M"]
Y = [98, 46, "M"]

categorical = [False, False, True]
ranges = [250, 90, 0]

print(distance(X, Y, categorical, ranges))

# Output: 0.963111111111111
"""