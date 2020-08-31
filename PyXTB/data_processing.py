import ujson, pandas
from PyXTB.settings import *


# def api_to_json(datas, filename):
#     with open(filename, 'wb') as f:
#         f.write(ujson.dumps(datas).encode(FORMAT))
        # logger.info(Fore.GREEN + f'datas successfully saved in {filename}')

def static_to_chartdataset(datas):
    i = 0
    df=dict()
    for key in datas:
        log.dataProc.spc_dbg(datas[key])
        if 'ChartRange' in key or 'ChartLast' in key:
            df[key] = pandas.DataFrame(datas[key]['returnData']['rateInfos'])
            i += 1
    return df




