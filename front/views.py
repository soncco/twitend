from django.shortcuts import render
from django_pandas.io import read_frame
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from base.models import Trends

from utils.vars import places

from urllib.parse import unquote

from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import json
import io
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
    pv = pd.pivot_table(df, index='hashtag', values=['position', 'tweets_counter'],
        aggfunc={'position': np.average, 'tweets_counter': max})
    
    newdf = pd.DataFrame(pv.to_records())
    try:
        newdf = newdf.sort_values(by=['position'])
    except:
        pass
    newdf = newdf.to_dict('records')

    horas = list(range(0,23))

    context = {
        'newdf': newdf,
        'location': location,
        'when': when,
        'fecha': arrow.get(fecha).datetime,
        'places': places(),
        'hour': hour,
        'location_data': location_data,
        'horas': horas
    }
    return render(request, 'front/index.html', context)


def indexxx(request, location='Peru', when='', hour=-1):
    location_data = next(item for item in places() if item['key'] == location)
    print(location_data)
    fecha_set = False
    if when == '':
        when = datetime.datetime.now()
        fecha2 = when - datetime.timedelta(hours=5)
        fecha1 = when - datetime.timedelta(hours=6)
    else:
        fecha_set = True
        when = datetime.datetime.strptime(when, '%Y-%m-%d')
        if hour == -1:
            hour = 5
        fecha2 = when - datetime.timedelta(hours=hour)
        fecha1 = when - datetime.timedelta(hours=hour+1)

    trends = Trends.objects.filter(
        location=location,
        trend_date__range=[fecha1, fecha2]
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

    horas = list(range(0,23))
    print(horas)

    context = {
        'newdf': newdf,
        'location': location,
        'when': when,
        'places': places(),
        'fecha_set': fecha_set,
        'horas': horas
    }
    return render(request, 'front/index.html', context)

def trend_stats(request, hashtag, location, date, hour):
    hour = datetime.datetime.strptime('%s %s:00:00' % (date, hour), '%Y-%m-%d %H:%M:%S')

    doce = hour - datetime.timedelta(hours=12)
    trend = Trends.objects.filter(
        location=location,
        hashtag=unquote(hashtag),
        trend_date__range=(doce, hour)
    )

    df = read_frame(trend)
    pvchart = pd.pivot_table(df, index='trend_date', columns='hashtag', values='tweets_counter', aggfunc=np.sum)
    newdf = pd.DataFrame(pvchart.to_records())

    return HttpResponse(newdf.to_json(), content_type='application/json')
