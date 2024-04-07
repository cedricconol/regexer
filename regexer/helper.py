import re
from io import StringIO

import pandas as pd

def extract_search_string(base_string, pattern):
    
    search_string = re.search(pattern, base_string)
    
    if search_string:
        return search_string.group(0)
    return None

def tester(csv_string, pattern, output='score', verbose=False):
    csv_sio = StringIO(csv_string)
    df = pd.read_csv(csv_sio, sep=",", header=0)

    score = 0
    total = 0
    result = []

    for _, row in df.iterrows():
        base_string = row['base_string']
        search_string = row['search_string']
        output_string = extract_search_string(base_string, pattern)
        result.append(output_string)

        total+=1

        if output_string == search_string:
            score+=1

        if verbose:
            print('Example number: ', total)
            print('base_string: ', base_string)
            print('output: ', output_string)
            print('expected: ', search_string)

            if output_string == search_string:
                print('result: ', 'correct')
                print('---')
            else:
                print('result: ', 'incorrect')
                print('---')
    
    if output=='score':
        return score/total
    
    if output=='dataframe':
        df['result'] = result
        df['is_correct'] = df.apply(lambda row: row.search_string==row.result, axis=1)
        return df