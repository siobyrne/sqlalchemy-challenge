# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///climate/resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
s = Base.classes.station
m = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

# add time variable for observational data
prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# landing page
@app.route("/")
def homepage():
    return f"""
        <h3>Routes:</h3>
        <ul>
       <li><a href="/api/v1.0/precipitation">Precipitation</a></li>
        <li><a href="/api/v1.0/stations">Stations</a></li>
        <li><a href="/api/v1.0/tobs">TOBS</a></li>
        </ul>
        <p>For the bottom two routes, replace <start_date> and
        <end_date> with a date in the format of YYYY-MM-DD.</p>
        <ul>
        <li>/api/v1.0/&lt;start_date&gt;</li>
        <li>/api/v1.0/&lt;start_date&gt;/&lt;end_date&gt;</li>
        </ul>
    """

# precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    rows = session.query(m.date, m.prcp).filter(m.date >= prior_year).order_by(m.date).all()
    precipitation = {_.date: _.prcp for _ in rows}
    session.close()
    return jsonify(precipitation)

# stations
@app.route("/api/v1.0/stations")
def stations():
    rows = session.query(
        s.station,
        s.name,
        s.latitude,
        s.longitude,
        s.elevation,
    )
    results = [
        {
            "station": _.station,
            "name": _.name,
            "latitude": _.latitude,
            "longitude": _.longitude,
            "elevation": _.elevation,
        }
        for _ in rows
    ]
    session.close()
    return jsonify(results)

# most active stations
@app.route("/api/v1.0/tobs")
def most_active():
    rows = (
        session.query(m.station, s.name, m.date, m.prcp, m.tobs)
        .filter(m.station == "USC00519281")
        .filter(m.date >= prior_year)
        .join(s, m.station == s.station)
        .all()
    )
    mas = [
        {
            "station": _.station,
            "name": _.name,
            "date": _.date,
            "temp_obs": _.tobs,
            "precipitation": _.prcp,
        }
        for _ in rows
    ]
    session.close()
    return jsonify(mas)

# pick a start date
@app.route("/api/v1.0/<start_date>")
def date(start_date):
    data = session.query(func.min(m.tobs), func.max(m.tobs), func.avg(m.tobs)).\
        filter(m.date >= start_date).all()

    session.close()

    data_list = list(np.ravel(data))

    temp_min=data_list[0]
    temp_max=data_list[1]
    temp_avg=data_list[2]

    output=(f"From date {start_date}, the minimum temperature is {temp_min}, the max temperature is {temp_max}, and the average temperature is {temp_avg}.")

    return jsonify(output)

# pick a start and end date
@app.route("/api/v1.0//<start_date>/<end_date>")
def dates(start_date, end_date=prior_year):
    data = session.query(func.min(m.tobs), func.max(m.tobs), func.avg(m.tobs)).\
        filter(m.date >= start_date).\
        filter(m.date <= end_date).all()
   
    session.close()

    data_list = list(np.ravel(data))

    temp_min=data_list[0]
    temp_max=data_list[1]
    temp_avg=data_list[2]

    output=(f"For the time period {start_date} to {end_date}, the minimum temperature is {temp_min}, the max temperature is {temp_max}, and the average temperature is {temp_avg}.")

    return jsonify(output)

# close session
session.close()

# run file
if __name__ == "__main__":
    app.run()