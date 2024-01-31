from flask import Flask, render_template, url_for, request, flash, redirect, send_from_directory, jsonify
import pandas as pd
import folium
import ssl
import folium.plugins as plugins
import os
from werkzeug.utils import secure_filename
import datetime
import joblib as jb
from pycaret.time_series import *

app = Flask(__name__, template_folder='templates')
UPLOAD_FOLDER = os.path.join(os.getcwd(),'upload')

ssl._create_default_https_context = ssl._create_unverified_context


#modelo = jb.load('modelo.pkl.z')
#forecast = jb.load('forecast.pkl')

@app.route("/")
def index():

    # Extrair o ano, mês e dia
    data_atual = datetime.datetime.now()
    data_atual = data_atual.strftime("%Y%m%d")

    # Scraping dos dados na fonte
    tabela = pd.read_csv(f"https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/focos_diario_{data_atual}.csv")

    # Manipulação dos dados de monitoramento
    # tabela = tabela.loc[tabela["estado"] == "ESPÍRITO SANTO"]
    tabela.drop(["id", "satelite", "municipio_id", "estado_id", "pais_id", "numero_dias_sem_chuva", "precipitacao",
         "risco_fogo", "bioma"], axis=1, inplace=True)
    tabela['data_hora_gmt'] = tabela['data_hora_gmt'].str.replace('T','\n').astype(str)
    tabela.to_excel(r'C:\Users\helio\OneDrive\Área de Trabalho\Projeto TCC\dadosTESTE.xlsx', index=False)
    dados = pd.read_excel(r"C:\Users\helio\OneDrive\Área de Trabalho\Projeto TCC\dadosTESTE.xlsx")

    # Separando as coordenadas do dataframe em uma lista
    coordenadas = []
    for latitude, longitude in zip(dados.lat.values[:1000], dados.lon.values[:1000]):
        coordenadas.append([latitude, longitude])

    # Separando os municípios do dataframe em uma lista
    municipios = dados['municipio'].tolist()

    # Separando os horários de registro do dataframe em uma lista
    data = dados['data_hora_gmt'].tolist()

    # Criando o mapa
    mapa = folium.Map(
        location=[-14.22, -50.3381],
        zoom_start=4
    )

    # Adicionando os focos de queimada no mapa
    for i in range(0, len(coordenadas)):
        folium.Marker(
            location=coordenadas[i],
            popup=f'Município: {municipios[i]}\n\nRegistro: {data[i]}\n\nCoordenadas: {coordenadas[i]}',
            tooltop='Clique aqui!',
            icon=folium.Icon(color='red')
        ).add_to(mapa)
    mapa.add_child(plugins.HeatMap(coordenadas))

    # Salvando o mapa
    mapa.save('templates/mapa.html')
    return render_template('home.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        file = request.files['arquivo']
        savePath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(savePath)
        print('Upload feito com sucesso!')
    return render_template('upload.html')

@app.route('/mapa')
def mapa():
    return render_template('mapa.html')

@app.route('/modelo')
def teste():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)