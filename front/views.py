from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models.functions import Lower

from django_pandas.io import read_frame

from base.models import Trends

from front.utils import change_col_name, get_globales

from utils.vars import places

from urllib.parse import unquote

import pandas as pd
import numpy as np
import datetime
import arrow

def index(request, location='Peru', when='', hour=-1):
    # Obteniendo data del location.
    try:
        location_data = next(item for item in places() if item['key'] == location)
    except:
        HttpResponseRedirect(reverse('front:index'))

    # Obteniendo data UTC.
    if when == '':
        utcnow = arrow.utcnow()
        utcprev = utcnow.shift(hours=-1)
    else:
        if hour == -1:
            utcnow = arrow.get(when, 'YYYY-MM-DD')
            utcprev = utcnow.shift(hours=-1)
        else:
            utcnow = arrow.get('%s %s:0:0' % (when, hour+1), 'YYYY-MM-DD H:m:s')
            utcprev = utcnow.shift(hours=-1)

    fecha = utcnow
    if hour == -1:
        utcnow = utcnow.shift(hours=location_data['shift'])
        utcprev = utcprev.shift(hours=location_data['shift'])


    trends = Trends.objects.filter(
        location=location,
        trend_date__range=[utcprev.datetime, utcnow.datetime]
    )
    print(trends.query)

    df = read_frame(trends)
    #df.to_csv('trends.csv')

    pv = pd.pivot_table(df, index='hashtag', values=['position', 'tweets_counter'],
        aggfunc={'position': np.average, 'tweets_counter': max})
    
    newdf = pd.DataFrame(pv.to_records())

    try:
        newdf = newdf.sort_values(by=['position'])
    except:
        pass
    newdf = newdf.to_dict('records')

    horas = list(range(0,23))

    q = request.GET.get('q', '')

    context = {
        'newdf': newdf,
        'location': location,
        'when': when,
        'fecha': arrow.get(fecha).datetime,
        'places': places(),
        'hour': hour,
        'location_data': location_data,
        'horas': horas,
        'q': q
    }
    return render(request, 'front/index.html', context)

def search(request):
    q = request.GET.get('q', '')
    q = q.strip()

    trends = Trends.objects.filter(hashtag__icontains=q)

    df = read_frame(trends)
    df['trend_date'] = df['trend_date'].map(lambda f: arrow.get(f).date())

    pv = pd.pivot_table(df, index=['hashtag', 'location'], values='tweets_counter',
        aggfunc=[np.average, 'count'])
    newdf = pd.DataFrame(pv.to_records())
    newdf.reset_index()
    newdf.fillna(0)
    new_cols = newdf.columns.values
    new_cols = [change_col_name(a) for a in new_cols]
    newdf.columns = new_cols
    #newdf.to_csv('test.csv', index=False)

    context = {
        'newdf': newdf.to_dict('records'),
        'q': q
    }
    return render(request, 'front/search.html', context)

def trend(request, hashtag):
    q = request.GET.get('q', '')

    trends = Trends.objects.filter(hashtag=hashtag)
    df = read_frame(trends)
    first = df['hashtag'][0]
    df['trend_date'] = df['trend_date'].map(lambda f: arrow.get(f).date())
    df['hashtag'] = df['hashtag'].map(lambda h: first)
    pv = pd.pivot_table(df, index=['hashtag', 'location'], columns='trend_date', values='tweets_counter', aggfunc=np.average)

    newdf = pd.DataFrame(pv.to_records())
    newdf.reset_index()
    newdf.fillna(0)

    globales = get_globales()

    context = {
        'globales': globales,
        'hashtag': hashtag,
        'newdf': newdf.to_dict('records'),
        'q': q
    }

    newdf.to_csv('hashtag.csv', index=False)
    return render(request, 'front/trend.html', context)


def acerca(request):
    
    return render(request, 'front/acerca.html')
