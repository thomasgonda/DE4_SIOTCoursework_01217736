import pandas as pd


def load_data_weather(filepath):
    # Function to load in the weather data from CSVs

    weather_df = pd.DataFrame()

    new_weather = pd.read_csv(filepath, header=None, parse_dates=[0])
    weather_df = weather_df.append(new_weather)

    # Name Columns
    weather_df.columns = ['datetime', 'weather'] #see in data preprocess naming

    # Convert to datetime
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], format='%Y-%m-%d %H:%M:%S.%f')

    # Sort chronologically
    weather = weather_df.sort_values(by='datetime')
    weather.set_index(['datetime'], inplace=True)

    return weather

def load_data_twitter(filepath):
    # Function to load in the twitter data from CSVs

    twitter_df = pd.DataFrame()

    # Import Twitter Data
    new_twitter = pd.read_csv(filepath, header=None, parse_dates=[0], usecols=[0, 1, 2])
    twitter_df = twitter_df.append(new_twitter)
    # Name Columns
    twitter_df.columns = ['datetime', 'sentiment', 'text']
    # Convert to datetime
    twitter_df['datetime'] = pd.to_datetime(twitter_df['datetime'], format='%Y/%m/%d %H:%M:%S')

    # Sort chronologically
    twitter = twitter_df.sort_values(by='datetime')
    twitter.set_index(['datetime'], inplace=True)

    return twitter