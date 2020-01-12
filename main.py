from os.path import dirname, join
from flask import Flask
from helpers import load_data_weather, load_data_twitter

from flask import render_template, request
#from Blameit import weather, twitter, app
from nltk.corpus import stopwords  # to get a list of stopwords
from nltk.tokenize import word_tokenize  # to split sentences into words
from collections import Counter  # to get words-frequency
import json  # to convert python dictionary to string format
from dashboards import Dashboards
import numpy
from sentiment import get_sentiment
from sklearn.impute import SimpleImputer
import numpy as np
from datetime import time,datetime

# Import the data
weather = load_data_weather(join(dirname(__file__), 'data', 'Data_Weather.csv'))
twitter = load_data_twitter(join(dirname(__file__), 'data', 'Data_Tweets.csv'))

app = Flask(__name__)  # create the app
app._static_folder=join(dirname(__file__), 'static')  # make the static folder discoverable
app.secret_key = 'SHH!'

dashes = Dashboards()
Sentiment = get_sentiment(twitter)

@app.route('/', methods=['GET'])
@app.route('/home/', methods=['GET'])
def index():
    return render_template('home.html', title='Home')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', title='About')

@app.route('/timeline', methods=['GET'])
# Page to display the collected data
def timeline():
    # sample the data into bins
    twitter['count'] = 1  # create count column
    bin = '60T'
    twitter_binned = twitter.resample(bin).sum()
    twitter_binned = twitter_binned.replace(0, numpy.NaN)

    # Imputation to fill missing data
    imputer = SimpleImputer(missing_values=np.NaN, strategy='mean')
    imputer = imputer.fit(twitter_binned)
    twitter_imputed = imputer.transform(twitter_binned)

    twitter_binned['count'] = twitter_imputed  # Insert the imputed data

    # create the plots
    script, div = dashes.dashboard_timeline(weather, twitter_binned, Sentiment)

    return render_template("timeline.html", the_div=div, the_script=script, title='Timeline')


@app.route('/prediction')
def prediction():
   return render_template('prediction.html', title = 'Prediction')


@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
        result = request.form
        print(result)
        now_time=datetime.strptime(result["Time"], '%H:%M')
        end_time = datetime.strptime('23:00', '%H:%M')
        start_time = datetime.strptime('07:00', '%H:%M')

        if now_time >= start_time and now_time <= end_time:
            message = "That's a good time to send out marketing materials"
        else:
            message = "That's not a good time to send out marketing materials"

        return render_template("result.html",result = result, title = 'Results', message=message)


@app.route('/analysis', methods=['GET'])
def analysis():

    # sample the data into bins
    twitter['count'] = 1  # create count column
    bin = '60T'
    twitter_binned = twitter.resample(bin).sum()
    twitter_binned = twitter_binned.replace(0, numpy.NaN)
    weather_binned = weather.resample('60T').mean()

    # Imputation to fill missing data
    imputer = SimpleImputer(missing_values=np.NaN, strategy='mean')
    imputer = imputer.fit(twitter_binned)  # twitter
    twitter_imputed = imputer.transform(twitter_binned)
    twitter_binned['count'] = twitter_imputed  # Insert the imputed data

    imputer = SimpleImputer(missing_values=np.NaN, strategy='mean')
    imputer = imputer.fit(weather_binned)  # weather
    weather_imputed = imputer.transform(weather_binned)

    weather_binned['weather_level'] = weather_imputed  # Insert the imputed data

    # create the plots
    script1, div1, script2, div2, script3, div3, correlation = dashes.dashboard_analysis(weather_binned, twitter_binned, Sentiment)
    corr_weather_twitter = "{0:.3f}".format(round(correlation[0],2))
    corr_weather_senti = "{0:.3f}".format(round(correlation[1],2))

    return render_template('analysis.html', the_div_1=div1, the_script_1=script1,
                           the_div_2=div2, the_script_2=script2, the_div_3=div3, the_script_3=script3,title='Analysis',
                           corr_weather_senti=corr_weather_senti, corr_weather_twitter=corr_weather_twitter)


@app.route('/insights', methods=['GET'])
def insights():
    return render_template('insights.html', title='Insights')


@app.route('/word_cloud', methods=['GET'])
def word_cloud():
    try:
        sentences = " "
        for tweet in twitter.text:
            sentences = sentences + " " + tweet

        # split sentences into words
        words = word_tokenize(sentences)
        # get stopwords
        stop_words = set(stopwords.words('english'))

        # remove stopwords from our words list and also remove any word whose length is less than 3
        # stopwords are commonly occuring words like is, am, are, they, some, etc.
        words = [word for word in words if word not in stop_words and len(word) > 2]

        # now, get the words and their frequency
        words_freq = Counter(words)

        # JQCloud requires words in format {'text': 'sample', 'weight': '100'}
        # so, lets convert out word_freq in the respective format
        words_json = [{'text': word, 'weight': count} for word, count in words_freq.items()]
        # now convert it into a string format and return it
        return json.dumps(words_json)

    except Exception as e:
        return '[]'


if __name__ == '__main__':
    app.run(port=5000, debug=True)