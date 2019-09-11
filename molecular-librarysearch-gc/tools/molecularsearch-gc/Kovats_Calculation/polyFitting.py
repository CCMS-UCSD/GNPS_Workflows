import numpy as np
import pandas as pd

def getParams(inputF,cosineScore,error,lib,minimumFeature,window_start,window_end):
    # parse the argument
    def search(lib,row):
        if row['INCHI'] in lib:
            return lib[row['INCHI']]
        return -1
    df = pd.read_csv(inputF,sep='\t')
    # filter out by cosinScore
    df = df[df.MQScore > cosineScore]
    # search for ki average
    lib_df = pd.read_csv(lib)
    lib_df = lib_df[lib_df.polarity.str.contains('non-polar')]
    lib = pd.Series(lib_df.ki_nonpolar_average.values,index=lib_df.INCHI.values).to_dict()
    df['ki_average'] = df.apply(lambda row:search(lib,row),axis = 1)
    df = df[df.ki_average>0]

    #clean the data for polynomial fitting:
    df = df[df['ki_average']>500]
    duration = df.RT_Query.max()
    df = df[df.RT_Query<=window_end]
    df = df[df.RT_Query>=window_start]
    #print(end,start)
    #df = df[df.RT_Query<800]
    if len(df) < minimumFeature:
        return None
    #simply find the polynomial fitting
    p_a = np.polyfit(df.RT_Query,df.ki_average,3)
    print(len(df))
    # we fit it twice to have more robust results:
    df =df[abs(df.ki_average-np.polyval(p_a,df.RT_Query))/np.polyval(p_a,df.RT_Query)<error]
    print(len(df))
    p_b = np.polyfit(df.RT_Query,df.ki_average,2)
    return p_b
