# dependencies
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# db setup
engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

# table references
Measurement = Base.classes.measurement
Station = Base.classes.station

# app setup
app = Flask(__name__)

# app routes
@app.route("/")
def home():
    return (
        f"Welcome! Available routes:</br></br>"
        f"All precipitation data:</br>"
        f"/api/v1.0/precipitation</br></br>"
        f"A list of stations:</br>"
        f"/api/v1.0/stations</br></br>"
        f"Temperature Observation (TOBS) for the most active station in the latest 12 months of data:</br>"
        f"/api/v1.0/tobs</br></br>"
        f"Min/Max/Avg TOBS for range starting from date formatted 'YYYY-MM-DD':</br>"
        f"/api/v1.0/YYYY-MM-DD</br></br>"
        f"Min/Max/Avg TOBS for range with a start and end date formatted 'YYYY-MM-DD/YYYY-MM-DD':</br>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    results = session.query(Measurement.station, Measurement.date, Measurement.prcp).all()
    session.close()

    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    all_names = list(np.ravel(results))
    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').filter(Measurement.date > '2016-08-22').all()
    session.close()

    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/YYYY-MM-DD")
def start_text():
    return (
        f"Enter date as formatted.</br></br>"
        f"For example:</br>"
        f"/api/v1.0/2015-04-24"
    )


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = session.query(Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.station).all()
    session.close()

    tobs_list = []
    for station, min, max, avg in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["min"] = min
        tobs_dict["max"] = max
        tobs_dict["avg"] = avg
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/YYYY-MM-DD/YYYY-MM-DD")
def start_end_text():
    return (
        f"Enter date as formatted.</br></br>"
        f"For example:</br>"
        f"/api/v1.0/2015-04-28/2016-05-13"
    )


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    results = session.query(Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).\
        group_by(Measurement.station).all()
    session.close()

    tobs_list = []
    for station, min, max, avg in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["min"] = min
        tobs_dict["max"] = max
        tobs_dict["avg"] = avg
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


if __name__ == '__main__':
    app.run(debug=True)