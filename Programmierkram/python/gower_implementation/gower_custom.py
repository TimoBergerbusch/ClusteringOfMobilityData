# Origin | Destination | Reason | Mean of Transportation | Average Time | Time Interval | Duration | Distance | Age | Gender


categorical = [True, True, True, True, False, True, False, False, False, True]

def distance (X, Y, categorical):
    # Check array sizes
    
    if (len(X) != len(Y)):
           print("Array sizes do not Match!")
           return;
    
    # Algorithm
    
    s = [0 for i in range(len(X))]
    
    ranges = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
       
    for i in range(len(X)):
        if (categorical[i] == True):
            s[i] = 1 if (X[i] == Y[i]) else 0
        else:
            s[i] = 1 - abs(X[i] - Y[i]) / ranges[i]
            
    return sum(s)/len(X) 
    
