from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "API Adala-News en ligne 🎉"

@app.route("/api/actus")
def get_actus():
    # Récupérer le numéro de page depuis les paramètres de requête (page=1 par défaut)
    page = int(request.args.get('page', 1))
    articles_per_page = 10  # Nombre d'articles par page
    url = "https://adala-news.fr/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Faire la requête pour récupérer la page web
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')

        # Calculer l'indice de début et de fin pour la pagination
        start = (page - 1) * articles_per_page
        end = start + articles_per_page
        paginated_articles = articles[start:end]

        result = []
        for article in paginated_articles:
            h2 = article.find('h2')
            a_tag = article.find('a')

            if h2 and a_tag:
                title = h2.get_text(strip=True)
                link = a_tag['href']

                # Chercher l'image dans un <a> avec un attribut `data-bgset` ou `style`
                img_tag = article.find('a', class_='penci-image-holder')
                image = ""
                if img_tag:
                    # Chercher l'URL dans l'attribut `data-bgset` ou `style`
                    img_url = img_tag.get('data-bgset') or ""
                    if not img_url:
                        # Si `data-bgset` est vide, on vérifie le style (background-image)
                        style = img_tag.get('style', "")
                        if 'background-image' in style:
                            img_url = style.split('url("')[1].split('")')[0]

                    # Si l'URL de l'image est relative, on la complète
                    image = urljoin(url, img_url) if img_url else ""

                result.append({
                    "titre": title,
                    "lien": link,
                    "image": image
                })

        return jsonify(result)
    else:
        return jsonify({"error": f"Erreur {response.status_code} lors de la récupération des données."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
