import os, time

pair = 'LUNABUSD'
period = '5m'
month = '03'


for i in range(1,30):

    si = str(i)
    if i < 10:
        si = '0' + si


    url = 'https://data.binance.vision/data/spot/daily/klines/%s/%s/%s-%s-2022-%s-%s.zip' % (pair, period, pair, period,month,si)
    fname = '%s-%s-2022-%s-%s.zip' % (pair, period, month, si)
    full_fname = '%s-%s-2022-%s.csv' % (pair, period, month)

    full_url = url
    print('downloading %s ...' % full_url)
    os.system('wget ' + full_url)
    os.system('unzip ' + fname)
    os.system('rm ' + fname)
    os.system('cat %s >> %s' % (fname.replace('.zip','.csv'),full_fname))
    os.system('rm ' + fname.replace('.zip','.csv'))

    print('waiting 3 seconds ....')
    time.sleep(3.0)

