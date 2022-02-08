from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from config import FLASK_KEY, BEARER_TOKEN, NEWS_API_KEY
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = FLASK_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
toolbar = DebugToolbarExtension(app)


base_url = 'https://api.twitter.com/2/tweets/search/recent'
headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}

# Newsapi
# base_url = 'https://newsapi.org/v2/everything/'
# headers = {'X-Api-Key': NEWS_API_KEY}


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/search')
def handle_search():
    q = request.args['q']
    # TWITTER:
    res = requests.get(f'{base_url}', headers=headers, '
                       params={'query': q, 'max_results': 10, 'tweet.fields'=[]})
    data = res.json()
    tweets = data['data']

    # tweets = data['sources']
    return render_template('index.html', tweets=tweets)

    # NEWSAPI
    # res = requests.get(f'{base_url}', headers=headers,
    #                    params={
    #                        'language': 'en',
    #                        'from': '2022-02-03',
    #                        'q': q,
    #                        'searchIn': 'title'
    #                    })
    # data = res.json()
    # stories = data['articles']
    # return render_template('index.html', stories=stories)

# NEWSAPI RESPONSE
# {
#     'status': 'ok',
#     'totalResults': 8039,
#     'articles':
#         [
#             {
#                 'source': {'id': 'wired', 'name': 'Wired'},
#                 'author': 'Gian M. Volpicelli',
#                 'title': 'As Kazakhstan Descends into Chaos, Crypto Miners Are at a Loss',
#                 'description': 'The central Asian country became No. 2 in the world for Bitcoin mining. But political turmoil and power cuts have hit hard, and the future looks bleak.'  ,
#                 'url': 'https://www.wired.com/story/kazakhstan-cryptocurrency-mining-unrest-e  ,
#                 'urlToImage': 'https://media.wired.com/photos/61de2d453e654a13e9a16ef0/191:100/w_1280,c_limit/Business_Kazakhstan-2HDE52K.jpg'  ,
#                 'publishedAt': '2022-01-12T12:00:00Z',
#                 'content': 'When Denis Rusinovich set up cryptocurrency mining company Maveric Group in Kazakhstan in 2017, he thought he had hit the jackpot. Next door to China and Russia, the country had everything a Bitcoin … [+4140 chars]'    },


# TWITTER RESPONSE
# {
#     'data':
#         [
#             {'id': '1489062762655453184', 'text': 'RT @ AirdropStario:  Metagwara Token Airdrop Task:          ➕},
#             {'id': '1489062762537836547', 'text': '@ Bitcoin AltSwitch(ALTS) \nThe mother of all rewards tokens is final},
#             {'id': '1489062761019629572', 'text': '@ Benzinga @ ElliotLane10 @ BzCannabis @ JavierHasse FATOSHI \nAudited by},
#             {'id': '1489062760973361157', 'text': 'RT @ satsandtitties: Eventually normies will complain about how unfair},
#             {'id': '1489062760747089923', 'text': 'RT @ hoseins51979372: @ davidgokhshtein @ InuSaitama Huuuuge News!!!\nNe},
#             {'id': '1489062760621170691', 'text': 'RT @ BitcoinMagazine: JUST IN - NYDIG CEO: "We are seeing more traditi},
#             {'id': '1489062759971328001', 'text': '@ ICOAnnouncement I am really happy to participate this project\n@Rase},
#             {'id': '1489062758796644356', 'text': 'RT @ yassineARK: A conversation about Bitcoin between Cathie Wood, Jac}
#         ],
#     'meta':
#         {'newest_id': '1489062762655453184', 'oldest_id': '1489062757060132865', 'result_count': 10, 'next_token': 'b26v89c19zqg8o3fpe48wcj7w2ffsz1qs6pxefymwmmwt'}}
