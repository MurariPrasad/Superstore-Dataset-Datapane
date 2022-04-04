import datapane as dp
import pandas as pd
import plotly.graph_objs as go
from plotly import subplots
import sqlite3 as sql3

#SQLite DB connection and table fetch
conn= sql3.connect('shop.db')
conn.text_factory=str
cursor= conn.execute(" select * from shop_record")

#creating pandas dataframe using fetched table
cols=[c[0] for c in cursor.description]
df=pd.DataFrame.from_records(data=cursor.fetchall(),columns=cols)

#altering dtypes of columns
df['Postal Code'] = pd.to_numeric(df['Postal Code'])
df['Sales'] = pd.to_numeric(df['Sales'])
df['Profit'] = pd.to_numeric(df['Profit'])
df['Quantity'] = pd.to_numeric(df['Quantity'])
df['Order Date']= pd.to_datetime(df['Order Date'])
df['Ship Date']= pd.to_datetime(df['Ship Date'])

""" SALES & PROFIT by DAY PLOTS"""
def figure0():
    df['year'] = df['Order Date'].dt.year
    df['month'] = df['Order Date'].dt.month
    df['dow'] = df['Order Date'].dt.dayofweek
    df['day'] = df['Order Date'].dt.day

    def gen_scatter(t,col,name):
        return go.Scatter(x=df.groupby(t)[col].sum().index,
                    y=df.groupby(t)[col].sum().values,
                    name=name)

    f0 = subplots.make_subplots(rows=4, cols=1)
    f0.append_trace(gen_scatter('year','Sales','by Year'), 1, 1)
    f0.append_trace(gen_scatter('month','Sales','by Month'), 2, 1)
    f0.append_trace(gen_scatter('dow','Sales','by Day of the Week'), 3, 1)
    f0.append_trace(gen_scatter('day','Sales','by Day of the Month'), 4, 1)
    f0['layout'].update(title={'text': 'Total Sales', 'x': 0.5, 'xanchor': 'center'}, showlegend=True)

    f0b = subplots.make_subplots(rows=4, cols=1)
    f0b.append_trace(gen_scatter('year', 'Profit', 'by Year'), 1, 1)
    f0b.append_trace(gen_scatter('month', 'Profit', 'by Month'), 2, 1)
    f0b.append_trace(gen_scatter('dow', 'Profit', 'by Day of the Week'), 3, 1)
    f0b.append_trace(gen_scatter('day', 'Profit', 'by Day of the Month'), 4, 1)
    f0b['layout'].update(title={'text': 'Total Profits', 'x': 0.5, 'xanchor': 'center'}, showlegend=True)
    return f0,f0b

"""SALE & PROFIT by REGION PLOTS"""
def figure1():
    def gen_scatter(region,col):
        return go.Scatter(
                x=df[df.Region == region].groupby('month')[col].sum().index,
                y=df[df.Region == region].groupby('month')[col].sum().values,
                name=region)

    data1 = [
        gen_scatter('West','Sales'),
        gen_scatter('East','Sales'),
        gen_scatter('Central','Sales'),
        gen_scatter('South','Sales'),
    ]
    data2= [
        gen_scatter('West','Profit'),
        gen_scatter('East','Profit'),
        gen_scatter('Central','Profit'),
        gen_scatter('South','Profit'),
    ]
    layout1 = go.Layout(
        title={
            'text': "Total Sales by Region",
            'x': 0.5,
            'xanchor': 'center'},
        xaxis={'title': 'Month'},
        yaxis={'title': 'Sales'}
    )
    layout2 = go.Layout(
        title={
            'text': "Total Profit by Region",
            'x': 0.5,
            'xanchor': 'center'},
        xaxis={'title': 'Month'},
        yaxis={'title': 'Profits'}
    )
    f1 = go.Figure(data=data1, layout=layout1)
    f1b = go.Figure(data=data2, layout=layout2)
    return f1,f1b

"""SALE & PROFIT by CITY PLOTS"""
def figure2():
    top_cities = df.groupby('City')['Quantity'].sum().sort_values(ascending=False)[:10].index
    def DATA(col):
        return df[df.City.isin(top_cities)].pivot_table(index="City",columns="dow",values=col,
                     aggfunc=lambda x:x.mean())

    fsale = go.Heatmap(z=DATA('Sales').values,
                    x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    y=DATA('Sales').index.values,
                    colorbar={'title': 'Sales'})
    fprofit = go.Heatmap(z=DATA('Profit').values,
                   x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday','Sunday'],
                   y=DATA('Profit').index.values,
                   colorbar={'title': 'Profits'})
    d1=[fsale]
    d2=[fprofit]
    layout1 = go.Layout(title={
        'text': "Total Sales by City",
        'x':0.5,
        'xanchor': 'center'})
    layout2 = go.Layout(title={
        'text': "Total Profit by City",
        'x':0.5,
        'xanchor': 'center'})

    f2 = go.Figure(data=d1, layout=layout1)
    f2b = go.Figure(data=d2, layout=layout2)
    return f2,f2b

"""SALE & PROFIT by SEGMENT PLOTS"""
def figure3():
    def gen_bar(seg,col):
        return go.Bar(
                x=df[df.Segment==seg].groupby('month')[col].sum().index,
                y=df[df.Segment==seg].groupby('month')[col].sum().values,
                name = seg,)

    d1=[
        gen_bar('Consumer','Sales'),
        gen_bar('Corporate', 'Sales'),
        gen_bar('Home Office', 'Sales')
    ]
    d2=[
        gen_bar('Consumer', 'Profit'),
        gen_bar('Corporate', 'Profit'),
        gen_bar('Home Office', 'Profit')
    ]

    layout1= go.Layout(
        title={
            'text': "Total Sales - Segmented",
            'x':0.5,
            'xanchor': 'center'},
        xaxis = {'title': 'Month'},
        yaxis = {'title': 'Sales'},
        barmode = 'stack')
    layout2= go.Layout(
        title={
            'text': "Total Profits - Segmented",
            'x':0.5,
            'xanchor': 'center'},
        xaxis = {'title': 'Month'},
        yaxis = {'title': 'Profits'},
        barmode ='stack')

    f3 = go.Figure(data=d1, layout=layout1)
    f3b = go.Figure(data=d2, layout=layout2)
    return f3,f3b

"""SALE & PROFIT by CATEGORY (%) PLOTS"""
def figure4():
    d1= go.Pie(labels=df.groupby('Category')['Sales'].sum().index,
              values=df.groupby('Category')['Sales'].sum().values,  hole = .2)
    d2= go.Pie(labels=df.groupby('Category')['Profit'].sum().index,
              values=df.groupby('Category')['Profit'].sum().values,  hole = .2)

    layout1= go.Layout(
        title={
            'text': "Total Sales by Category (%)",
            'x':0.5,
            'xanchor': 'center'})
    layout2= go.Layout(
        title={
            'text': "Total Profit by Category (%)",
            'x':0.5,
            'xanchor': 'center'})

    f4= go.Figure(data=d1, layout=layout1)
    f4b= go.Figure(data=d2, layout=layout2)
    return f4,f4b

"""SALE & PROFIT by SUB-CATEGORY (%) PLOTS"""
def figure5():
    d1= go.Pie(labels=df.groupby('Sub-Category')['Sales'].sum().index,
              values=df.groupby('Sub-Category')['Sales'].sum().values,  hole = .2)
    d2= go.Pie(labels=df.groupby('Sub-Category')['Profit'].sum().index,
              values=df.groupby('Sub-Category')['Profit'].sum().values,  hole = .2)

    layout1= go.Layout(
        title={
            'text': "Total Sales by Sub-Category (%)",
            'x':0.5,
            'xanchor': 'center'}, legend={'orientation': 'h'})
    layout2= go.Layout(
        title={
            'text': "Total Profit by Sub-Category (%)",
            'x':0.5,
            'xanchor': 'center'}, legend={'orientation': 'h'})

    f5= go.Figure(data=d1, layout=layout1)
    f5b = go.Figure(data=d2, layout=layout2)
    return f5,f5b

"""SALE & PROFIT by SUB-CATEGORY PLOTS"""
def figure6():
    d1= go.Bar(y=df.groupby('Sub-Category')['Sales'].sum().index,
            x=df.groupby('Sub-Category')['Sales'].sum().values,
            orientation='h')
    d2= go.Bar(y=df.groupby('Sub-Category')['Profit'].sum().index,
            x=df.groupby('Sub-Category')['Profit'].sum().values,
            orientation='h')

    layout1 = go.Layout(
        title={
            'text': "Total Sales by Sub-Category",
            'x': 0.5,
            'xanchor': 'center'},
        xaxis={'title': 'Sales'})
    layout2= go.Layout(
        title={
            'text': "Total Profit by Sub-Category",
            'x':0.5,
            'xanchor': 'center'},
        xaxis={'title': 'Profit'})

    f6= go.Figure(data=d1,layout=layout1)
    f6b= go.Figure(data=d2,layout=layout2)
    return f6,f6b

"""
***********************************************************************************************************************
"""

#Calling the above functions to generate analytic plots
fig0,fig0b = figure0()
fig1,fig1b = figure1()
fig2,fig2b = figure2()
fig3,fig3b = figure3()
fig4,fig4b = figure4()
fig5,fig5b = figure5()
fig6,fig6b = figure6()

#Describing and generating the HTML for this report and adding the above plots to this.
banner_html = """<div style="padding: 20px;display: flex;align-items: center;font-size: 40px;color: #0066cc;background: #e0ebeb;">
<img src="https://upload.wikimedia.org/wikipedia/en/thumb/d/d1/Aldi_Sud_logo.svg/100px-Aldi_Sud_logo.svg.png" style="margin-right: 1em; max-height: 250px;">
<h2>Sales and Profits Analysis</h2>
</div>
"""

dp.Report(
    dp.HTML(banner_html),
    dp.Select(
        type=dp.SelectType.TABS,
        blocks=[
                dp.Group(
                    dp.Select(
                        dp.Plot(fig0, label='Sales by Day'),
                        dp.Plot(fig1, label='Sales by Region'),
                        dp.Plot(fig2, label='Sales by City'),
                        dp.Plot(fig3, label='Sales by Segment'),
                        dp.Plot(fig4, label='Sales by Category (%)'),
                        dp.Plot(fig5, label='Sales by Sub-Category (%)'),
                        dp.Plot(fig6, label='Sales by Sub-Category')),
                    label="Sales Analysis Charts"
                    ),
                dp.Group(
                    dp.Select(
                        dp.Plot(fig0b, label='Profit by Day'),
                        dp.Plot(fig1b, label='Profit by Region'),
                        dp.Plot(fig2b, label='Profit by City'),
                        dp.Plot(fig3b, label='Profit by Segment'),
                        dp.Plot(fig4b, label='Profit by Category (%)'),
                        dp.Plot(fig5b, label='Profit by Sub-Category (%)'),
                        dp.Plot(fig6b, label='Profit by Sub-Category')),
                    label="Profit Analysis Charts"
                    )
            ])
).save(name="Analysis",path='Analysis.html',open=True)
conn.close()
