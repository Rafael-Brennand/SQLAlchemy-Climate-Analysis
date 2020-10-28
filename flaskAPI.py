import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# 3. Define static routes
@app.route("/")
def home():
    return (
        f"Welcome to the Weather API!<br/>"
        f"Here are the available routes:<br/>"
        f"Precipitation data: /api/v1.0/precipitation<br/>"
        f"Station data: /api/v1.0/stations<br/>"
        f"Temperature data: /api/v1.0/tobs"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    #Query precipitations
    last_year = session.query(measurement.date, measurement.prcp).filter(measurement.date >= '2016-08-23').all()
    session.close()
    #Make it into a dictionary
    prcp = {date: prcp for date, prcp in last_year}

    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    stat_session = Session(engine)
    #Query stations
    stat_results = stat_session.query(station.station, station.name).all()
    stat_session.close()
    # Convert list of tuples into normal list
    stat_names = list(np.ravel(stat_results))
    return jsonify(stat_names)

@app.route("/api/v1.0/tobs")
def tobs():
    tobs_session = Session(engine)
    #Query
    tobs_results = tobs_session.query(measurement.date, measurement.tobs, measurement.station).filter_by(station = "USC00519281").filter(measurement.date >= '2016-08-23').all()
    tobs_session.close()
    
    all_temps = []
    for date, tobs, station in tobs_results:
        temp_dict = {}
        temp_dict['date'] = date
        temp_dict['tobs'] = tobs
        temp_dict['station'] = station
        all_temps.append(temp_dict)
    
    return jsonify(all_temps)

@app.route("/api/v1.0/<start>")
def temp_info_by_start(start):
    session = Session(engine)

    start_results = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).group_by(measurement.date).all()
    session.close()
    #Convert to list
    #start_list = list(np.ravel(start_results))
    #return jsonify(start_list)

    dates = []
    for result in start_results:
        date_dict = {}
        date_dict['date'] = result[0]
        date_dict['min temp'] = result[1]
        date_dict['avg temp'] = result[2]
        date_dict['max temp'] = result[3]
        dates.append(date_dict)
    
    return jsonify(dates)

@app.route("/api/v1.0/<start>/<end>")
def temp_info_by_start_end(start,end):
   session = Session(engine)

   start_end_results = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start, measurement.date <= end).group_by(measurement.date).all()
   session.close()

   dates = []
   for result in start_end_results:
       date_dict = {}
       date_dict['date'] = result[0]
       date_dict['min temp'] = result[1]
       date_dict['avg temp'] = result[2]
       date_dict['max temp'] = result[3]
       dates.append(date_dict)

   return jsonify(dates)

    


# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)