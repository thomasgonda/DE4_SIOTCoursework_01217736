import pandas as pd
from sklearn.impute import SimpleImputer
import numpy as np


def get_sentiment(data):
    # Function to calculate sentiment score per hour

    # Group data by hour
    sent_df = data.groupby([pd.Grouper(freq='H'),data.sentiment], axis=0).size().reset_index(name='count')

    # Add the missing datetime rows between 2018-12-22 13:00:00 and 2018-12-23 11:00:00
    dates_to_add = pd.date_range(start='2020-01-06 14:00:00', end='2020-01-12 10:00:00', freq='H') #HERE TO BE MODIFIED
    length = len(dates_to_add)
    senti = np.empty(length)
    senti[:] = np.nan
    to_add = {'datetime':dates_to_add, 'sentiment': senti, 'text':senti}
    df_to_add = pd.DataFrame(data = to_add)
    new_df = (sent_df.append(df_to_add, sort=True, ignore_index=True))
    sent_df = new_df.sort_values(by='datetime')

    # Add the missing datetime rows between 2018-12-31 12:00:00 and 2019-01-01 13:00:00
    dates_to_add = pd.date_range(start='2020-01-06 14:00:00', end='2020-01-12 10:00:00', freq='H') #ERE TO BE MODIFIED
    length = len(dates_to_add)
    senti = np.empty(length)
    senti[:] = np.nan
    to_add = {'datetime':dates_to_add, 'sentiment': senti, 'text':senti}
    df_to_add = pd.DataFrame(data = to_add)
    new_df = (sent_df.append(df_to_add, sort=True, ignore_index=True))
    sent_df = new_df.sort_values(by='datetime')

    sentiment = pd.DataFrame()  # Empty dataframe

    # drop incomplete hour
    sent_df = sent_df.drop([0, 1], axis = 0)
    i = 1

    for index, row in sent_df.iterrows():  # Loop to store positive, negative and neutral scores in a single row in the dataframe

        if i == 1:
            Negative = row['count']
            i = i + 1

        elif i == 2:
            Neutral = row['count']
            i = i + 1

        elif i == 3:
            Positive = row['count']
            Hour = row['datetime']
            newrow = pd.DataFrame({'datetime': Hour, 'Positive': Positive, 'Negative': Negative, 'Neutral': Neutral},
                                  index=[0])
            sentiment = sentiment.append(newrow)
            i = 1

    scores = []
    for index, row in sentiment.iterrows():  # Score calculation loop for each hour
        top = row['Positive'] - row['Negative']
        bottom = row['Positive'] + row['Negative'] + row['Neutral']
        score = float(top / bottom)
        scores.append(score)

    sentiment['Score'] = pd.Series(scores, index=sentiment.index)
    sentiment = sentiment.set_index('datetime')

    # Imputation to fill missing data
    imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
    imputer = imputer.fit(sentiment[['Score']])
    sent_imputed = imputer.transform(sentiment[['Score']])
    sentiment['Score'] = sent_imputed  # Insert the imputed data

    return sentiment