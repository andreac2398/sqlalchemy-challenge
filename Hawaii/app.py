# Import the dependencies.
# 1. import Flask
import numpy as np
import sqlalchemy
import datetime as dt
from flask import Flask, jsonify
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func , and_
from sqlalchemy.ext.automap import automap_base


#################################################
# Database Setup
#################################################
database_path = Path("../Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{database_path}")

# reflect an existing database into a new model
# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
M = Base.classes.measurement
S = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def homepage():
    return '''
        <h1> Welcome to the Hawaii Climate APP </h1>
        <h2> This are all the Avalible routes</h2>
        <ul>
        <li>/api/v1.0/precipitation</li>
        <li>/api/v1.0/stations</li>
        <li>/api/v1.0/tobs</li>
        <li>/api/v1.0/[start]</li>
        <li>/api/v1.0/[start]/[end]</li>
        </ul>
        <a> Remember the date format is MMDDYYYY </a>
'''

@app.route('/api/v1.0/precipitation')
def precipitation():
    results = session.query(M.date , M.prcp).filter(M.date >= '2016-08-23').all()
    session.close()
    return jsonify([{'Date':d,'Precipitation':p} for d,p in results ])

@app.route('/api/v1.0/stations')
def stations():
    results = list(np.ravel(session.query(S.station).all()))
    session.close()
    return jsonify(results)

@app.route('/api/v1.0/tobs')
def tobs():
    active_station = 'USC00519281'
    results = session.query(M.date, M.tobs).filter(M.date >= '2016-08-23').filter(M.station == active_station).all()
    session.close()
    return jsonify([{'Date':d,'Temperature':t} for d,t in results ])

@app.route('/api/v1.0/<start_date>')
def start(start_date):
    start_date = dt.datetime.strptime(start_date, "%m%d%Y")
    results = session.query(func.min(M.tobs), func.max(M.tobs), func.avg(M.tobs)).filter(M.date >= start_date).all()
    session.close()
    start_date_tobs =[]
    for min, avg, max in results:
        date_dict = {}
        date_dict["Min_Temp"] = min
        date_dict["Max_Temp"] = max
        date_dict["Avg_Temp"] = avg
        start_date_tobs.append(date_dict)
    return jsonify(start_date_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    start_date = dt.datetime.strptime(start_date, "%m%d%Y")
    end_date = dt.datetime.strptime(end_date, "%m%d%Y")
    results = session.query(func.min(M.tobs), func.max(M.tobs), func.avg(M.tobs))\
        .filter(M.date >= start_date).filter(M.date <= end_date).all()
    session.close()
    start_end_tobs =[]
    for min, avg, max in results:
        date_dict = {}
        date_dict["Min_Temp"] = min
        date_dict["Max_Temp"] = max
        date_dict["Avg_Temp"] = avg
        start_end_tobs.append(date_dict)
    return jsonify(start_end_tobs)

if __name__ == '__main__':
    app.run()
