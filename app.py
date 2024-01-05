# Import the dependencies.
from flask import Flask, render_template, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import json

import os 
#################################################
# Database Setup
#################################################
app = Flask(__name__)
with app.app_context():
   basedir = os.path.abspath(os.path.dirname(__file__))
   app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'Resources/hawaii.sqlite')
   app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

 # reflect an existing database into a new model
   db = SQLAlchemy(app) 

# reflect the tables
   Base = automap_base()
   Base.prepare(db.engine, reflect=True)

# Save references to each table
   Station = Base.classes.station
   Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
   session = db.Session(db.engine)
   

#################################################
# Flask Setup
#################################################
app.config['DEBUG'] = True
# app.config['TEMPLATE_AUTO_RELOAD'] = True


with app.app_context():
   recent_date = session.query(func.max(Measurement.date)).scalar()
   recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
   one_year_later = recent_date - dt.timedelta(days=365)

   active_station = session.query(Measurement.station, func.count(Measurement.station).label('measurement_count')
                               ).group_by(Measurement.station).order_by(desc('measurement_count')).first()

#################################################
# Flask Routes
#################################################

@app.route('/api/v1.0/precipitation')
def get_all_precipitaion_in_last_12M():

   results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=one_year_later.date())
   #  return jsonify(dict(results))
   return render_template("view.htm", data=json.dumps(dict(results)))

@app.route('/api/v1.0/stations')
def get_all_station():
   results = session.query(Station.station, Station.name).all()
   # return jsonify(dict(results))
   return render_template("view.htm", data=json.dumps(dict(results)))


@app.route('/api/v1.0/tobs')
def get_all_acitve_station():
  
   results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=one_year_later.date(), Measurement.station == active_station[0])
   # return jsonify(dict(results))
   return render_template("view.htm", data=json.dumps(dict(results)))


@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def get_all_min_max_avg_temp(start, end=None):
   start = dt.datetime.strptime(start, "%Y-%m-%d").date()
  

   results = []
   if(end):
      end = dt.datetime.strptime(end, "%Y-%m-%d").date()
      results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)
                                 ).where(Measurement.date >= start, Measurement.date <=end).first()
   else:
      results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)
                                 ).where(Measurement.date >= start).first()
   
   print(results)
   # return jsonify({"min":results[0], 'max':results[1], 'avg':results[2]})
   return render_template("view.htm", data=json.dumps({"min":results[0], 'max':results[1], 'avg':results[2]}))



@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return render_template("index.html", data = "<h3>No data on home page</h3>")




if __name__ == '__main__':
   app.run(debug=False)