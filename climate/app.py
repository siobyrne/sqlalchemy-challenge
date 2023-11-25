# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

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

@app.route("/api/v1.0/precipitation")
def precipitation():
    rows = session.query(m.date, m.prcp).filter(m.date >= prior_year).order_by(m.date).all()
    precipitation = {_.date: _.prcp for _ in rows}
    session.close()
    return jsonify(precipitation)

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



# close session
session.close()

# run file
if __name__ == "__main__":
    app.run()