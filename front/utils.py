from django_pandas.io import read_frame

from base.models import Trends

import pandas as pd
import numpy as np
import datetime
import arrow

def change_col_name(col_name):
    col_name = col_name.replace("('", '')
    col_name = col_name.replace("', 'tweets_counter')", '')
    return col_name

def get_globales():
    utcnow = arrow.utcnow()
    utcprev = utcnow.shift(hours=-1)

    utcnow.shift(hours=-5)
    utcprev.shift(hours=-5)

    trends = Trends.objects.filter(
        trend_date__range=[utcprev.datetime, utcnow.datetime]
    )

    df = read_frame(trends)

    pv = pd.pivot_table(df, index='hashtag', values=['position', 'tweets_counter'],
        aggfunc={'position': np.average, 'tweets_counter': max})
    
    newdf = pd.DataFrame(pv.to_records())

    try:
        newdf = newdf.sort_values(by=['position'])
    except:
        pass
    newdf = newdf.to_dict('records')
    return newdf