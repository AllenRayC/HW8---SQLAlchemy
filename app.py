import numpy as np
import pandas as pd

import datetime as dt
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

# Save references to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    precipitation_dict = []
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.station == 'USC00519397').all()
    USC00519397_df = pd.DataFrame(results).set_index("date")
    USC00519397_df.columns = ['USC00519397']
    USC00519397_dict = USC00519397_df.to_dict()
    precipitation_dict.append(USC00519397_dict)
    
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.station == 'USC00513117').all()
    USC00513117_df = pd.DataFrame(results).set_index("date")
    USC00513117_df.columns = ['USC00513117']
    USC00513117_dict = USC00513117_df.to_dict()
    precipitation_dict.append(USC00513117_dict)
    
    return (
        jsonify(precipitation_dict)
    )

@app.route("/api/v1.0/stations")
def stations():
    
    # Query all stations
    results = session.query(Station).all()
    
    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for station in results:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        all_stations.append(station_dict)
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365.25)

    # Perform a query to retrieve the tobs
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > year_ago).all()

    return jsonify(results)

@app.route("/api/v1.0/<start>")
def start(start):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date > start_date).all()
    
    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date > start_date).filter(Measurement.date < end_date).all()
    
    return jsonify(results)


@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )


if __name__ == "__main__":
    app.run(debug=True)
