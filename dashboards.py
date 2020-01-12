from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.layouts import column
import statsmodels.api as sm
import numpy as np

class Dashboards:

    def dashboard_timeline(self, data_weather, data_twitter_binned, sentiment):
        # Function to create plots for the timeline page

        #source_weather = {'datetime':data_weather.index, 'weather_level':data_weather['weather_level']}
        data_weather['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data_weather.index]
        data_twitter_binned['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data_twitter_binned.index]
        sentiment['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in sentiment.index]

        print('data weather', data_weather)
        print('data twitter', data_twitter_binned)
        source_weather = ColumnDataSource(data_weather)
        source_twitter = ColumnDataSource(data_twitter_binned)
        print('source_weather', source_weather)
        print('source_twitter', source_twitter)

        # Create weather-Time plot
        plot_weather = self.create_plot_weather(source_weather, 'weather', 'datetime', 'temperature')

        # Create Twitter-Time Plot
        plot_twitter = self.create_plot_twitter(source_twitter, 'Tweet Incidence', 'DateTime',
                                                'Tweet Incidence per Hour (no. of tweets)', plot_weather)

        # Create sentiment-Time Plot
        plot_sentiment = self.create_plot_sentiment(sentiment, 'sentiment Score', plot_weather)

        # create grid of plots
        layout = column([plot_weather, plot_twitter, plot_sentiment])
        script, div = components(layout)

        return script, div

    def dashboard_analysis(self, data_weather_binned, data_twitter_binned, sentiment):
        # Function to create plots for the analysis page

        # ACF plot weather
        allTimeLags, autoCorr ,selectedLagPoints, selectedAutoCorr= self.acf(data_weather_binned)
        source_weather_acf = ColumnDataSource({'x1': np.array(allTimeLags), 'y1': np.array(autoCorr)})
        source_weather_acf_selected = ColumnDataSource({'x2': np.array(selectedLagPoints), 'y2':np.array(selectedAutoCorr)})
        acf_plot_weather = self.create_acf_plot(source_weather_acf, source_weather_acf_selected, 'Apparent Temperature ACF', plot=None)

        # ACF Plot Twitter
        allTimeLags, autoCorr, selectedLagPoints, selectedAutoCorr = self.acf(data_twitter_binned)
        source_twitter_acf = ColumnDataSource({'x1': allTimeLags, 'y1': autoCorr})
        source_twitter_acf_selected = ColumnDataSource({'x2': np.array(selectedLagPoints), 'y2': np.array(selectedAutoCorr)})
        acf_plot_twitter = self.create_acf_plot(source_twitter_acf, source_twitter_acf_selected, 'Tweet Incidence ACF', plot=None)

        # ACF Plot sentiment
        allTimeLags, autoCorr, selectedLagPoints, selectedAutoCorr = self.acf(sentiment)
        source_sentiment_acf = ColumnDataSource({'x1': np.array(allTimeLags), 'y1': np.array(autoCorr)})
        source_sentiment_acf_selected = ColumnDataSource({'x2': np.array(selectedLagPoints), 'y2': np.array(selectedAutoCorr)})
        acf_plot_sentiment = self.create_acf_plot(source_sentiment_acf, source_sentiment_acf_selected, 'Tweet sentiment ACF', plot=None)

        # Both datasets together and normalised
        norm_weather = (data_weather_binned['weather_level'] - np.mean(data_weather_binned['weather_level'])) / np.std(
            data_weather_binned['weather_level'])
        norm_twitter = (data_twitter_binned['count'] - np.mean(data_twitter_binned['count'])) / np.std(data_twitter_binned['count'])
        norm_sentiment = (sentiment['Score']-np.mean(sentiment['Score'])) / np.std(sentiment['Score'])

        # load into normalised dataframes
        norm_weather_cds = ColumnDataSource({'datetime': np.array(data_weather_binned.index), 'weather_level': np.array(norm_weather)})
        norm_twitter_cds = ColumnDataSource({'datetime': np.array(data_twitter_binned.index), 'count': np.array(norm_twitter)})
        norm_sentiment_cds = ColumnDataSource({'datetime':np.array(sentiment.index), 'score':np.array(norm_sentiment)})

        # Normalised Plot
        norm = self.create_norm_plot(norm_weather_cds, norm_twitter_cds, norm_sentiment_cds, 'Normalised Datasets')

        # Labels for tooltips
        data_twitter_binned['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data_twitter_binned.index]
        sentiment['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in sentiment.index]

        # Trends seasonality and noise
        weather_decomposed = sm.tsa.seasonal_decompose(norm_weather, freq=24)  # The frequency is daily
        #tooltip = [x.strftime("%Y-%m-%d %H:%M:%S") for x in weather_decomposed.trend.index]
        l_trend = ColumnDataSource({'datetime': np.array(weather_decomposed.trend.index), 'y': np.array(weather_decomposed.trend)})
        l_seasonal = ColumnDataSource({'datetime': np.array(weather_decomposed.seasonal.index), 'y': np.array(weather_decomposed.seasonal)})
        l_noise = ColumnDataSource({'datetime': np.array(weather_decomposed.resid.index), 'y': np.array(weather_decomposed.resid)})

        twitter_decomposed = sm.tsa.seasonal_decompose(norm_twitter, freq=24)  # The frequency is daily
        t_trend = ColumnDataSource({'datetime': np.array(twitter_decomposed.trend.index), 'y': np.array(twitter_decomposed.trend)})
        t_seasonal = ColumnDataSource({'datetime': np.array(twitter_decomposed.seasonal.index), 'y': np.array(twitter_decomposed.seasonal)})
        t_noise = ColumnDataSource({'datetime': np.array(twitter_decomposed.resid.index), 'y': np.array(twitter_decomposed.resid)})

        sentiment_decomposed = sm.tsa.seasonal_decompose(norm_sentiment, freq=24)  # The frequency is daily
        s_trend = ColumnDataSource({'datetime': np.array(sentiment_decomposed.trend.index), 'y': np.array(sentiment_decomposed.trend)})
        s_seasonal = ColumnDataSource({'datetime': np.array(sentiment_decomposed.seasonal.index), 'y': np.array(sentiment_decomposed.seasonal)})
        s_noise = ColumnDataSource({'datetime':sentiment_decomposed.resid.index, 'y': np.array(sentiment_decomposed.resid)})

        trend = self.create_seasonality_plot(l_trend, t_trend, s_trend, 'Trend', None)
        seasonality = self.create_seasonality_plot(l_seasonal, t_seasonal, s_seasonal, 'Seasonality', None)
        noise = self.create_seasonality_plot(l_noise, t_noise, s_noise, 'Noise', None)

        # Correlation of datasets
        corr_weather_twitter = norm_weather.corr(norm_twitter)
        corr_weather_senti = norm_weather.corr(norm_sentiment)
        correlation = [corr_weather_twitter, corr_weather_senti]

        # Create layouts
        trends = column([trend, seasonality, noise])
        layout = column([acf_plot_weather, acf_plot_twitter, acf_plot_sentiment])

        # Scripts and divs to return
        script1, div1 = components(norm)
        script2, div2 = components(layout)
        script3, div3 = components(trends)

        return script1, div1, script2, div2, script3, div3, correlation

    def create_plot_weather(self, source, title, x_name, y_name,hover_tool=None,
                         width=1100, height=300):
        # Function to create weather plots for the timeline page

        plot = figure(title=title,plot_width=width,
                      plot_height=height,
                      min_border=0, toolbar_location="above", tools=['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save', 'hover'],
                      outline_line_color="#666666", x_axis_type='datetime',
                      x_axis_label=x_name, y_axis_label=y_name)

        hover = plot.select(dict(type=HoverTool))
        tips = [('Date', '@tooltip'), ('weather Level (lx)', '$y')]
        hover.tooltips = tips
        hover.mode = 'vline'

        plot.line(x='datetime', y='weather', line_width=2, source=source)

        return plot

    def create_plot_twitter(self, source, title, x_name, y_name, plot,
                         width=1100, height=300):
        # Function to create twitter plots for the timeline page

        plot = figure(title=title,plot_width=width,
                      plot_height=height,
                      min_border=0, toolbar_location="above", tools=['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save', 'hover'],
                      outline_line_color="#666666", x_axis_type='datetime',
                      x_axis_label=x_name, y_axis_label=y_name, x_range=plot.x_range)

        hover = plot.select(dict(type=HoverTool))
        tips = [('Date', '@tooltip'), ('Tweets per Hour', '$y')]
        hover.tooltips = tips
        hover.mode = 'vline'

        plot.line(x='datetime', y='count', line_width=2, source=source)

        return plot

    def create_plot_sentiment(self, source, title, plot,
                         width=1100, height=300):
        # Function to create sentiment plots for the timeline page

        plot = figure(title=title, plot_width=width,
                      plot_height=height,
                      min_border=0, toolbar_location="above", tools=['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save', 'hover'],
                      outline_line_color="#666666", x_axis_type='datetime',
                      x_axis_label='Datetime', y_axis_label='Tweet sentiment Score', x_range=plot.x_range)

        hover = plot.select(dict(type=HoverTool))
        tips = [('Date', '@tooltip'), ('sentiment Score', '$y')]
        hover.tooltips = tips
        hover.mode = 'vline'

        plot.line(x='datetime', y='Score', line_width=2, source=source)

        return plot

    def create_acf_plot(self, source, select_source, title, plot,
                         width=1100, height=300):
        # Function to create acf plots for the analysis page

        plot = figure(title=title,plot_width=width,
                      plot_height=height,
                      min_border=0, toolbar_location="above", tools=['save'],
                      outline_line_color="#666666",
                      x_axis_label='Time Lag (Hours)', y_axis_label='Correlation Coefficient')

        plot.line(x='x1', y='y1', line_width=2, source=source)


        plot.add_tools(HoverTool(
            tooltips=[
                ('Timelag', '@x1{f} hours'),
                ('Correlation Coefficient', '@y1{0.2f}'),
            ],

            # display a tooltip whenever the cursor is vertically in line with a glyph
            mode='vline'))

        plot.circle(x='x2', y='y2', source=select_source, size=5)

        return plot

    def create_norm_plot(self, source_weather, source_twitter, source_sentiment, title,
                         width=1100, height=300):
        # Function to create normalised plots for the analysis page

        plot = figure(title=title,plot_width=width,
                      plot_height=height,
                      min_border=0, toolbar_location="above", tools=['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save'],
                      outline_line_color="#666666", x_axis_type='datetime',
                      x_axis_label='Date')

        plot.line(x='datetime', y='weather_level', line_width=2, source=source_weather, legend_label='Apparent Temperature')
        plot.line(x='datetime', y='count', line_width=2, line_color="red", source=source_twitter, legend_label='Twitter Count')
        plot.line(x='datetime', y='score', line_width=2, line_color="green", source=source_sentiment, legend_label='Tweet sentiment Score')

        plot.legend.click_policy = "hide"  # interactive legend

        return plot

    def create_seasonality_plot(self, source1, source2, source3, title, xlabel,
                         width=1100, height=300):
        # Function to create seasonality plots for the analysis page

        plot = figure(title=title, plot_width=width,
                      plot_height=height,
                      min_border=0, toolbar_location="above", tools=['save', 'pan', 'wheel_zoom', 'reset'],
                      outline_line_color="#666666", x_axis_type = 'datetime',
                      x_axis_label=xlabel)

        plot.line(x='datetime', y='y', line_width=2, source=source1, legend_label='Apparent Temperatures')
        plot.line(x='datetime', y='y', line_width=2, source=source2, line_color='red', legend_label='Twitter Count')
        plot.line(x='datetime', y='y', line_width=2, source=source3, line_color='green', legend_label='Tweet sentiment')

        plot.legend.click_policy = "hide"

        return plot

    def acf(self, data):
        # Function to calculate acf for the analysis page

        # Change to a one column data series
        data_series = data.iloc[:,0]

        selectedLagPoints = [24, 48, 72]  # points to highlight
        maxLagDays = 7
        allTimeLags = np.arange(1, maxLagDays * 24)

        autoCorr = [data_series.autocorr(lag=dt) for dt in allTimeLags]
        selectedAutoCorr = [data_series.autocorr(lag=dt) for dt in selectedLagPoints]

        return allTimeLags, autoCorr, selectedLagPoints, selectedAutoCorr