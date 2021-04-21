#Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
#Create engine
sql_engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect Database
D_base = automap_base()
D_base.prepare(sql_engine, reflect = True)

#Save table references
Measurement =D_base.classes.measurement
Station = D_base.classes.station

#Create session
sql_session = Session(sql_engine)

#Setup Flask
app = Flask(__name__)

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d'
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.

    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d

    Returns:
        TMIN, TAVG, and TMAX
    """

    return sql_session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

#Set Flask Routes

@app.route("/")
def main():
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""

    print("Received precipitation api request.")

    final_date = sql_session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")

    early_date = max_date - dt.timedelta(365)


    rainfall_data = sql_session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= early_date).all()

        results_dict = {}
    for result in rainfall_data:
        results_dict[result[0]] = result[1]

    return jsonify(results_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""

    print("Received station api request.")

#query stations list
    stations = sql_session.query(Station).all()

#create a list of dictionaries
        stations_list = []
        for station in stations:
            station_dict = {}
            station_dict["id"] = station.id
            station_dict["station"] = station.station
            station_dict["name"] = station.name
            station_dict["latitude"] = station.latitude
            station_dict["longitude"] = station.longitude
            station_dict["elevation"] = station.elevation
            stations_list.append(station_dict)

        return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
    def tobs():
        """Return a JSON list of temperature observations for the previous year."""

        print("Received tobs api request.")

#We find temperature data for the last year.  First we find the last date in the database
    final_date = sql_session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")

#create list of dictionaries (one for each observation)
    tobs_list = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
    def start(start):

        print("Received start date api request.")

#First we find the last date in the database
           final_date_query = sql_session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
           max_date = final_date_query[0][0]

#get the temperatures
            temps = calc_temps(start, max_date)

 #create a list
           json_list = []
           date_dict = {'start_date': start, 'end_date': max_date}
           json_list.append(date_dict)
           json_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
           json_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
           json_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

           return jsonify(json_list)

@app.route("/api/v1.0/<start>/<end>")
    def start_end(start, end):
        """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start
        or start-end range."""

        print("Received start date and end date api request.")

#get the temperatures
    temps = calc_temps(start, end)

#create a list
           json_list = []
           date_dict = {'start_date': start, 'end_date': end}
           json_list.append(date_dict)
           json_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
           json_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
           json_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

           return jsonify(json_list)

if __name__ == "__main__":
           app.run(debug = True)
