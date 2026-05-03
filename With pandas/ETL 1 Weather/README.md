# ETL 1 Weather

This project collects current weather data from the Open-Meteo API, processes it, and stores it in a local SQLite database.

## What the code does

- `main.py` retrieves weather data for a fixed location using a GET request to the Open-Meteo API.
- It extracts the `current_weather` section from the API response.
- The data is converted into a pandas DataFrame.
- Unnecessary columns are dropped and column names are cleaned up.
- The time value is parsed into a proper datetime format.
- Temperature and windspeed values are converted to floats and formatted with units (`°C` and `km/h`).
- The processed weather record is appended to a SQLite database file named `weather.db`.
- The code prints the latest weather data and the total number of records stored.

## Files

- `main.py`: main script that fetches, processes, and stores weather data.
- `weather.db`: local SQLite database created by `main.py`.
- `weather-dashboard/`: a separate dashboard project folder.

## Notes

- The code currently runs once when executed.
- There is commented-out scheduling code to run the weather check periodically.
- If scheduling is needed, uncomment the `schedule.every(15).minutes.do(check_weather)` line and the `schedule.run_pending()` loop.
