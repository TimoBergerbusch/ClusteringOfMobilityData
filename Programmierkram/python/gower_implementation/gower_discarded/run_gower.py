import gower
import testDataGenerator as dg
import pandas as pd
import numpy as np


# Steps from Timos Library
linesOfFile = dg.read_file()
linesOfContent = dg.clean_up_list(linesOfFile)
dataEntries = dg.parse_lines_of_content(linesOfContent)
data_collection = dg.DataCollection(dataEntries)

mask = [True,  # origin
        True,  # destination
        True,  # reason
        True,  # HMV
        True,  # RED
        True,  # mean of Transportation
        True,  # average Time
        True,  # duration
        True,  # distance
        True,  # age
        True,  # gender
        False,  # strata - NOTE: should stay False in order to test
        False  # denote whether an ID should be created
        ]

length = 5

data_collection_equal_dist = data_collection.equalDistribute(length)
data = data_collection_equal_dist.toDict(mask)
data_pd = pd.DataFrame(data)
print(data_pd)
#

categoricals = [False for key in data]
for i, key in enumerate(data):
    if key in {'reason', 'meanOfTransportation', 'gender'}:
        categoricals[i] = True

#categorical_features=np.array(categoricals)
D = gower.gower_distances(data_pd);
print(D, D.shape)
