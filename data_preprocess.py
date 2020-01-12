from os import listdir

# Get files to read from
path_to_dir = "C:/Users/Tom/Desktop/SIoT/Blameit/Blameit/data"
filenames = listdir(path_to_dir)
csvs = [filename for filename in filenames if filename.endswith(".csv")]
print(csvs)
# Open files to write to
l_out = open("Data_Weather.csv", "a")
t_out = open("Data_Tweets.csv", "a")

# Write to CSVs
for csv in csvs:
    # Insert Weather Data
    #print(csv)
    if "weather" in csv: #!!!! here we need to change the name of the thingy so that it corresponds to the same column name that we have applied in helpers
        print('hello')
        for line in open(path_to_dir + '/' + csv):
            # csv.next()
            l_out.write(line)

    # Insert Twitter Data
    elif "tweets" in csv: #!!! same thing here as above, column name in helpers
        for line in open(path_to_dir + '/' + csv):
            # csv.next()
            t_out.write(line)