import time
import requests
import pandas as pd
import sqlite3
import schedule
import os
def check_weather():

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "weather.db")

    r = requests.get("https://api.open-meteo.com/v1/forecast?latitude=14.594&longitude=121.032&current_weather=true")

    if r.status_code == 200:
        #store the result of request in variable data
        data = r.json()["current_weather"]
        
        df = pd.DataFrame([data])

        #drop the unnecessary columns and rename the column
        df.drop(columns=["weathercode", 'interval','is_day'], inplace=True)

        #rename the winddirection column to wind_direction
        df.rename(columns={'winddirection': 'wind_direction'}, inplace=True)

        #format the time
        df['time'] = pd.to_datetime(df['time'])
        
        #convert the temperature to float then map them and format them to 1 decimal place and add the unit °C, do the same for windspeed but add the unit km/h
        #so map in pandas behave differently then default map it accept one argument which is the funtion
        #.map(function, iterable/argument) = default python, iterable/argument.map(function) = pandas
        #so in here the map loops to each value in the temperature column and apply the function to it, 
        #the function is to format the value to 1 decimal place and add the unit °C, the same for windspeed but add the unit km/h
        df['temperature'] = df['temperature'].astype(float).map('{:.1f} °C'.format)
        df['windspeed'] = df['windspeed'].astype(float).map('{:.1f} km/h'.format)
        print(df)

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS weather (
            time TEXT,
            temperature TEXT,
            wind_direction TEXT,
            windspeed TEXT
        )
        ''')
        df.to_sql('weather', connection, if_exists='append', index=False)
        cursor.execute('SELECT * FROM weather')
        rows = cursor.fetchall()
        print("total records in database:", len(rows))
        connection.commit()
        connection.close()

# schedule.every(15).minutes.do(check_weather)

# check_weather()  # Run the function once at the start
if __name__ == "__main__":
    check_weather()
    # schedule.run_pending()
    # time.sleep(1)
    
