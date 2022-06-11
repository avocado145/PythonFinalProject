import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import sqlite3
import json
from pandas.core.groupby.groupby import DataError
sns.set()

st.title("Проект по визуализации данных")
"""В этой части приведем статистику по мишленовски ресторанам в разных городах мира в зависимости от количества звезд и полученных наград"""
st.markdown("""
<style>
.big-font {
    font-size:25px !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<p class="big-font">Мишленовский гид по ресторанам мира</p>', unsafe_allow_html=True)

df = pd.read_csv('michelin_my_maps.csv')

df['Award'] = df['Award'].str[:1]
# st.write(df.head())
# st.write(df.describe())
city_restaurants = pd.unique(df['Location'].values)
#st.write(city_restaurants)



columns = np.array(['All restaurants in the city', '1-STAR Restaurants in the city', '2-STAR Restaurants in the city',
                    '3-STAR Restaurants in the city', 'Restaurants with Bib Gourmand Award in the city',
                    'Distribution of restaurants'])
table = st.radio("Choose the information you would like to see", columns)
cities_to_choose = st.multiselect("Choose the town", city_restaurants)
df1 = df['Location'].value_counts().to_frame()
df_1star = df[df['Award'] == '1']['Location'].value_counts().to_frame()
df_2star = df[df['Award'] == '2']['Location'].value_counts().to_frame()
df_3star = df[df['Award'] == '3']['Location'].value_counts().to_frame()
df_baward = df[df['Award'] == 'B']['Location'].value_counts().to_frame()
df2 = df.groupby('Location')['Award'].value_counts()
# st.write(df2.head())
if (table == 'All restaurants in the city'):
    fig = plt.figure()
    figure, ax = plt.subplots()
    ax.set(xlabel='City', ylabel='All restaurants in the city')
    plt.bar(cities_to_choose, df1.loc[cities_to_choose, 'Location'])
    st.pyplot(plt, clear_figure=True)
elif (table == '1-STAR Restaurants in the city'):
    fig = plt.figure()
    figure, ax = plt.subplots()
    ax.set(xlabel='City', ylabel='1-STAR Restaurants in the city')
    try:
        plt.bar(cities_to_choose, df_1star.iloc[cities_to_choose, 'Location'])
        st.pyplot(plt, clear_figure=True)
    except IndexError:
        st.write("This city has no restaurants with such award")
elif (table == '2-STAR Restaurants in the city'):
    fig = plt.figure()
    figure, ax = plt.subplots()
    ax.set(xlabel='City', ylabel='2-STAR Restaurants in the city')
    try:
        plt.bar(cities_to_choose, df_2star.iloc[cities_to_choose, 'Location'])
        st.pyplot(plt, clear_figure=True)
    except IndexError:
        st.write("This city has no restaurants with such award")
elif (table == '3-STAR Restaurants in the city'):
    fig = plt.figure()
    figure, ax = plt.subplots()
    ax.set(xlabel='City', ylabel='3-STAR Restaurants in the city')
    try:
        plt.bar(cities_to_choose, df_3star.iloc[cities_to_choose, 'Location'])
        st.pyplot(plt, clear_figure=True)
    except IndexError:
        st.write("This city has no restaurants with such award")
elif (table == 'Restaurants with Bib Gourmand Award in the city'):
    fig = plt.figure()
    figure, ax = plt.subplots()
    ax.set(xlabel='City', ylabel='Restaurants with Bib Gourmand Award in the city')
    try:
        plt.bar(cities_to_choose, df_baward.iloc[cities_to_choose, 'Location'])
        st.pyplot(plt, clear_figure=True)
    except IndexError:
        st.write("This city has no restaurants with such award")
#нужно здесь допилить способ  добавления трех bar charts и distribution одновременно + вывести no information если
#у нас нет



st.title("Использование API")
"""В данной части проекта проанализируем с помощью API википедию(и не только) на тему мишленовских ресторанов и постараемся 
извлечь нужную нам информацию"""

"""Здесь с помощью названия ресторана и сервиса https://nominatim.openstreetmap.org/search через API можем найти точный
адрес нужного нам ресторана"""
entrypoint = "https://nominatim.openstreetmap.org/search"
selected_restaurants = df["Name"]
all_restaurants = st.multiselect("Select the restaurant", selected_restaurants)
# st.write(df.loc[df["Name"] == f'{all_restaurants[0]}']["Address"])
try:
    params = {'q': df.loc[df["Name"] == all_restaurants[0]]["Address"],
              'format': 'json'}
    r = requests.get(entrypoint, params=params)
    json = r.json()
    for i in json[0]:
        if (i == "display_name"):
            st.write(json[0][i])
        else:
            continue
except IndexError:
    st.write(" ")

st.write("--------------------------------------------------------------------------------------------")
"""Здесь можно посмотреть, какие есть статьи на википедии на тему ресторанов и увидеть, какие нам статьи могут быть
интересны в данном проекте"""
st.write("--------------------------------------------------------------------------------------------")
url = "https://ru.wikipedia.org/w/api.php"
params = {
    'action': 'query',
    'list': 'categorymembers',
    'cmtitle': "Категория:Рестораны",
    'format': 'json'
}
titles = []
while True:
    r = requests.get(url, params=params)
    data = r.json()
    titles.extend([cm['title'] for cm in data['query']['categorymembers']])
    if 'continue' not in data:
        break
    params.update(data['continue'])
for i in titles:
    st.write(i)

st.write("--------------------------------------------------------------------------------------------")
"""По нашей теме здесь как раз есть статьи The World’s 50 Best Restaurants, Обладатели «Звезды Мишлен» и 
Рестораны из рейтинга The World’s 50 Best Restaurants"""

st.title("Использование SQL")
st.write("В этой части возьмем совершенно другую выборку, которая предоставляет отзывы о ресторанах с всего мира. Попробуем найти среди данных отзывов - отзывы на Мишленовские рестораны и отранжировать их - в этой части могут возникнуть проблемы с sql, к сожалению(")

data_reviews = pd.read_csv("TA_restaurants_curated.csv")
conn = sqlite3.connect("review")
c = conn.cursor()
c.execute("""
    DROP TABLE IF EXISTS review;
""")
data_reviews.to_sql("review", conn)
"""Вывели какой-то отзыв"""
st.write(c.execute("""
    SELECT * FROM review
    limit 1;
""").fetchall())
"""Теперь возьмем нашу изначальную базу данных с Мишленовскими ресторанами и приведем ее в sql-формат"""

conn1 = sqlite3.connect("rest")
c1 = conn.cursor()
c1.execute("""
    DROP TABLE IF EXISTS rest;
""")
df.to_sql("rest", conn)
"""Вывели какой-то ресторан из старой выборки"""
st.write(c.execute("""
    SELECT * FROM rest
    limit 1;
""").fetchall())
st.write("--------------------------------------------------------------------------------------------")
"""Выведем рестораны с мишленовской звездой/другой наградой, на которых есть отрицательный отзыв(сделали это с помощью регулярных выражений!)"""
st.write(c.execute("""
    SELECT rest.Name,
     review.Reviews FROM review
    inner join rest on rest.Name = review.Name where review.Name is not NULL and review.Reviews LIKE '%awful%' or '%bad%' 
    or '%no%' or '%horrible%' or '%unpleasant%' or '%inferior%' or '%unsatisfactory%' or '%nasty%';
""").fetchall())
st.write("--------------------------------------------------------------------------------------------")
"""Выведем рестораны с мишленовской звездой/другой наградой, на которых есть положительный отзыв(сделали это с помощью регулярных выражений!) - выведем первые 5, так как их довольно много, но в следующем запросе
выведем количество положительных отзывов!"""
st.write(c.execute("""
    SELECT rest.Name,
     review.Reviews FROM review
    inner join rest on rest.Name = review.Name where review.Name is not NULL and review.Reviews LIKE '%good%' or '%wonderful%' 
    or '%great%' or '%super%' or '%tasty%' or '%best%' or '%worth%' or '%sweet%'
    limit 5;
""").fetchall())
st.write("--------------------------------------------------------------------------------------------")
st.write("Общее количество положительных отзывов")
st.write(c.execute("""
    SELECT COUNT(rest.Name),
     review.Reviews FROM review
    inner join rest on rest.Name = review.Name where review.Name is not NULL and review.Reviews LIKE '%good%' or '%wonderful%' 
    or '%great%' or '%super%' or '%tasty%' or '%best%' or '%worth%' or '%sweet%'
""").fetchall())
st.write("Общее количество положительных отзывов - 259, что уже сильно больше, чем 2 отрицательных отзыва. Из этого можем сделать вывод, что все же рестораны из нашей выборки не зря получили такие ценные награды")
