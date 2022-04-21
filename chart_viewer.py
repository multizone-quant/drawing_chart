# 
# chart 그리기
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/70
#

import json
import csv
from  datetime import datetime
import time
import pandas as pd
from plot import *
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import plotly.offline as py_offline
import plotly.graph_objs as go
from plotly import tools


# 첫 줄은 title이라고 가정, 이후에 title 값을 key로 갖는 dict로 읽기
def read_csv_to_dict(fname) :
    data = []
    keys =[]
    first = 1
    with open(fname, 'r', encoding='UTF8') as FILE :
        csv_reader = csv.reader(FILE, delimiter=',', quotechar='"')
        for row in csv_reader :
            if first : # make dict keys
                keys = row.copy()
                first = 0
            else :                
                data.append(get_new_item(keys, row))
    return data

def draw_chart_plotly(fname, ticker) :
    if 0 :
        data = read_csv_to_dict(fname)
        for each in data :
            pad = ''
            if len(each['time']) == 5 :
                pad = '0'
            each['date'] = each['dt'] + 'T' + pad + each['time']
        save_to_file_csv('lbhs_data1.csv', data)

    data = pd.read_csv(fname)

    # plotly를 이용하여 candelstkck에 text 출력하는 부분 설명한 글
    # https://info.cloudquant.com/2019/08/candlestick_plotly/

    annotations = []
   
    pre_text = ''
    for i in range(0, len(data))  :# 
        text = ''
        nega = 1
        loc = 'high'

        if data['action'][i] == 'buy' :
            text = 'B'
            nega = -1
            loc = 'low'
            pre_text = 'B'
        elif data['action'][i] == 'sell' :
            text = 'S'
            pre_text = 'S'
        elif data['action'][i] == 'skip' :
            text = 'X'
            pre_text = 'X'
        if text != '' :
            annotations.append(go.layout.Annotation(x=data['datetime'][i],
                                                    y=data[loc][i],
                                                    xshift=1,  # x 축 기준으로 오른쪽으로 x칸 이동
                                                    yshift=10*nega,  # y 축 기준으로 오른쪽으로 y칸 이동
                                                    showarrow=False,
                                                    text=text))
            if pre_text != 'X':
                annotations.append(go.layout.Annotation(x=data['datetime'][i],
                                                        y=data[loc][i],
                                                        xshift=1,  # x 축 기준으로 오른쪽으로 x칸 이동
                                                        yshift=25*nega,  # y 축 기준으로 오른쪽으로 y칸 이동
                                                        showarrow=False,
                                                        text=str(int(data['qty'][i])) + ',' + str(int(data['balance'][i]))))

    # draw할 layout 생성
    width = len(data) * 15
    layout = dict(
            title=ticker,
            xaxis=go.layout.XAxis(title=go.layout.xaxis.Title( text="Time"), rangeslider=dict (visible = False)),
            yaxis=go.layout.YAxis(title=go.layout.yaxis.Title( text="Price")),
            width=width,
            height=800,
            annotations=annotations
    )
    fig = go.Figure()
    data_candle = go.Candlestick(x=data.datetime,open=data.open,high=data.high,low=data.low,close=data.close)
    fig = go.Figure(data=[data_candle],layout=layout)

    # 계산한 ma7 그리기
    fig.add_trace(go.Scatter( x=data.datetime, y=data.ma7, name="MA7"))
    # 계산한 ma24 그리기
    fig.add_trace(go.Scatter( x=data.datetime, y=data.ma24, name="MA24"))

    fig.update_layout(title='..')

    fig.show()

# balance가 0이 될 때 누적 수익 출력
def print_summary(fname) :
    tr_history = read_csv_to_dict(fname)

    start_trading_date = ''
    num_trading = 0
    profit = 0
    balance = 0
    for each in tr_history:
        if each['action'] == '' or each['action'] == 'skip' :
            continue
        if start_trading_date == '' :
            start_trading_date = each['datetime']
        num_trading += 1
        if 1:
            # 매수가는 open + 0.05 매도가는 open - 0.05
            diff = 0.05
            nega = -1
            if each['action'] == 'sell' :
                diff = -0.05
                nega = 1
            exec_price = float(each['close']) + diff


        profit += (exec_price * int(each['qty']) * nega)
        balance = int(each['balance'])
        if balance == 0 :
            print(each['datetime'], profit)
    print('== result ==')
    position = '매수'
    if balance > 0 :
        position = '매도'

    last = tr_history[-1]
    print('  period    :', start_trading_date, last['datetime'])
    print('  # tradings: ', num_trading)
    print('  balance   : ', position, balance)
    # balance를 종가에 팔았다고 가정
    if balance != 0 :
        if 1:
            if balance > 0 : # 매수였으면 종가매도
                profit += (float(last['close'])*abs(balance))
            else : # 매도였으면 종가매수
                profit -= (float(last['close']*abs(balance)))

    print('  profit    : ', profit)

if __name__ == '__main__':

    fname = '.\\sim_end_ex.csv'
    ticker = 'mini future'
    print_summary(fname) 
    draw_chart_plotly(fname, ticker)
    print('end')
