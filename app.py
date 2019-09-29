from flask import Flask
from flask_bootstrap import Bootstrap
from flask import render_template
import pygal
from pygal.style import Style
import praw
from textblob import TextBlob
from datetime import date, timedelta

reddit = praw.Reddit(client_id='...', client_secret='...', username='...',
                     password='...', user_agent='...')

app = Flask(__name__)
bootstrap = Bootstrap(app)

random_subs = []
cur = 1

random_polarity = []
random_subjectivity = []
random_listy = []


@app.route('/')
def index():
    random_sub = generate_new()
    return render_template('user_three.html', rst=random_sub.title, rss=random_sub.selftext, next=len(random_subs) + 1,
                           cur=1, graph_data=pygalexample(cur),
                           rdate=(date.today() + timedelta(cur - 1)).strftime('%B %d, %Y'),
                           graph_data2=pygalexample2(cur))

def generate_new():
    random_sub = reddit.subreddit('CasualConversation').random() # change the subreddit
    random_subs.append(random_sub)
    random_sentiment = TextBlob(random_sub.selftext).sentiment
    random_polarity.append(random_sentiment.polarity)
    random_subjectivity.append(random_sentiment.subjectivity)

    rs_tags = TextBlob(random_sub.selftext).tags
    unique_rs_tags = set(rs_tag[1] for rs_tag in rs_tags)

    listy = {'CC': 0, 'CD': 0, 'DT': 0, 'EX': 0, 'FW': 0, 'IN': 0, 'JJ': 0, 'JJR': 0, 'JJS': 0, 'LS': 0, 'MD': 0,
             'NN': 0, 'NNS': 0, 'NNP': 0, 'NNPS': 0, 'PDT': 0, 'POS': 0, 'PRP': 0, 'PRP$': 0, 'RB': 0, 'RBR': 0,
             'RBS': 0, 'RP': 0, 'TO': 0, 'UH': 0, 'VB': 0, 'VBD': 0, 'VBG': 0, 'VBN': 0, 'VBP': 0, 'VBZ': 0, 'WDT': 0,
             'WP': 0, 'WP$': 0, 'WRB': 0}

    for tups in rs_tags:
        if listy.get(tups[1]) == None:
            print(tups[1])
        else:
            listy[tups[1]] = listy[tups[1]] + 1

    listy_merged = {}
    listy_merged_raw = [listy['JJ'], listy['JJR'], listy['JJS'], listy['RB'], listy['RBR'], listy['RBS'], listy['VB'],
                        listy['VBD'], listy['VBG'], listy['VBN'], listy['VBP'], listy['VBZ']]
    listy_merged_norm = [float(i) / sum(listy_merged_raw) for i in listy_merged_raw]
    random_listy.append(listy_merged_norm)

    return random_sub

def pygalexample(cur):
    custom_style = Style(
        value_font_size=20.0,
        tooltip_font_size=20.0,
        major_label_font_size=20.0,
        label_font_size=15.0,
        value_label_font_size=20.0
    )
    graph = pygal.Line(x_label_rotation=20, style=custom_style, dots_size=5, stroke_style={'width': 2}, range=(-1, 1))
    graph.title = '% Sentiment Analysis.'
    graph.y_title = 'Polarity [-1.0, 1.0],  Subjectivity [0.0,1.0]'
    random_dates = []
    for i in range(0, cur):
        random_dates.append(date.today() + timedelta(i))
    # graph.x_labels = range(1,cur+1)
    graph.x_labels = map(lambda d: d.strftime('%m/%d/%y'), random_dates)
    graph.add('Subjectivity', random_subjectivity[0:cur])
    graph.add('Polarity', random_polarity[0:cur])
    graph_data = graph.render_data_uri()
    return graph_data

def pygalexample2(cur):
    custom_style = Style(
        value_font_size=20.0,
        tooltip_font_size=20.0,
        major_label_font_size=20.0,
        label_font_size=15.0,
        value_label_font_size=20.0
    )
    radar_chart = pygal.Radar(style=custom_style)
    radar_chart.title = 'Part-of-Speech (POS) Tagging'
    radar_chart.x_labels = ['JJ', 'JJR', 'JJS', 'RR', 'RBR', 'RBS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    for i in range(cur):
        radar_chart.add((date.today() + timedelta(i)).strftime('%m/%d/%y'), random_listy[i])
    radar_chart_data = radar_chart.render_data_uri()
    return radar_chart_data


@app.route('/<int:num>')
def itemize(num):
    cur = num
    print(cur)
    print(len(random_subs) + 1)
    if (num < len(random_subs) + 1):
        return render_template('user_three.html', rst=random_subs[cur - 1].title, rss=random_subs[cur - 1].selftext,
                               next=len(random_subs) + 1, cur=cur, graph_data=pygalexample(cur),
                               rdate=(date.today() + timedelta(cur - 1)).strftime('%B %d, %Y'),
                               graph_data2=pygalexample2(cur))
    else:
        random_sub = generate_new()
        return render_template('user_three.html', rst=random_sub.title, rss=random_sub.selftext,
                               next=len(random_subs) + 1, cur=cur, graph_data=pygalexample(cur),
                               rdate=(date.today() + timedelta(cur - 1)).strftime('%B %d, %Y'),
                               graph_data2=pygalexample2(cur))


@app.errorhandler(500)
def internal_server_error(e):
    return itemize(cur), 500

if __name__ == '__main__':
    app.run()
