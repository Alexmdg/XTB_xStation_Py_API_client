import ujson, pandas
from api.settings import *


def api_to_json(datas, filename):
    with open(filename, 'wb') as f:
        f.write(ujson.dumps(datas).encode(FORMAT))
        # logger.info(Fore.GREEN + f'datas successfully saved in {filename}')

def static_to_chartdataset(datas):
    i = 0
    df=list(range(0, len(datas)))
    for key in datas:
        if 'ChartRange' in key:
            df[i] = pandas.DataFrame(datas[key]['returnData']['rateInfos'])
            i += 1
    return df




