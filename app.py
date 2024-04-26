import requests
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/noticias', methods=['POST'])
def get_crypto_news():
    API_KEY = 'b05e46ab630a94da404aae7e5f08b7e1c347b8695bf1224a6b3d0a3617ff3930'
    URL = 'https://min-api.cryptocompare.com/data/v2/news/?lang=EN'  # Asumiendo que este es el endpoint correcto
    fulfillment_text = ""
    # Realizar la solicitud a la API
    req = request.get_json()
    query_result = req.get('queryResult', {})
    parameters = query_result.get('parameters', {})
    crypto_name = req.get('sessionInfo', {}).get('parameters', {}).get('cryptoparam', '').lower()

    # Configuración de los parámetros para la solicitud a la API
    params = {
        'categories': crypto_name,
        'api_key': API_KEY
    }

    response = requests.get(URL, params=params)
    
    if response.status_code == 200:
        news_data = response.json()
        all_news = news_data.get('Data', [])

        # Filtrar noticias que contienen 'crypto_name' en el título o en el cuerpo
        filtered_news = [news for news in all_news if crypto_name.lower() in news['title'].lower() or crypto_name.lower() in news['body'].lower()]
        
        # Limitar a las primeras 3 noticias
        news_list = filtered_news[:3]
        
        # Formatear la información de las noticias
        news_info = []
        for news in news_list:
            time = datetime.fromtimestamp(news['published_on']).strftime('%Y-%m-%d %H:%M:%S')
            news_info.append({
                'title': news['title'],
                'date': time,
                'url': news['url']
            })

        if news_info:
            fulfillment_text += f"Estas son las últimas noticias sobre {crypto_name}\n--------------------------\n"
            for item in news_info:
                fulfillment_text += f"Title: {item['title']}\nDate: {item['date']}\nURL: {item['url']}\n--------------------------\n"
        else:
            fulfillment_text = "No hay noticias recientes de esta cryptomoneda"
    else:
        print("Error Code:", response.status_code)
        try:
            print("Error Body:", response.json()) 
        except ValueError:
            print("Error Body:", response.text)
        fulfillment_text = "Hubo un error al obtener las noticias de la cryptomoneda"
    
    return jsonify({
        "fulfillmentResponse": {
            "messages": [{
                "text": {
                    "text": [fulfillment_text]
                }
            }]
        }
    })



if __name__ == '__main__':
    app.run(port=5000, debug=True)
