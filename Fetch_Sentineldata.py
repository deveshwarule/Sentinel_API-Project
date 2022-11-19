from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from flask import jsonify, Flask,request,make_response,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import datetime

import os
Username = os.environ.get('username')
Password = os.environ.get('password')

api = SentinelAPI(Username, Password)
footprint = geojson_to_wkt(read_geojson('map.geojson'))

app = Flask(__name__)
db = SQLAlchemy(app)
ma = Marshmallow(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Sentinel_Data.sqlite'

class Sentinel_Data(db.Model):
    product_id = db.Column(db.Unicode(10),primary_key=True,unique=True)
    fileName = db.Column(db.String(500))
    cloudCovPer = db.Column(db.Numeric)
    st_date = db.Column(db.DateTime)
    en_date = db.Column(db.DateTime)
    Gen_date = db.Column(db.DateTime)

class Schema(ma.Schema):
    class Meta:
        fields = ("product_id", "fileName", "cloudCovPer", "st_date", "en_date","Gen_date")

my_Data = Schema(many=True)

@app.errorhandler(Exception)
def resource_not_found(e):
    return jsonify(Please_Check_With_Following_Error=str(e))

# -----------------------------------------------------------------------------------------
@app.route("/")
def Home():
    return "Data stored Sucessfully."

@app.route("/data")
def sentinelData():
    return render_template('main.html')

@app.route("/data/getdata", methods=['POST'])
def getdata():
        Satellite=request.form.get('Sentinel_sat')
        StartDate = request.form.get('Starting_date')
        EndDate = request.form.get('End_date')
        a = StartDate.split('-')
        b = EndDate.split('-')
        d1= datetime.datetime(int(a[0]),int(a[1]),int(a[2]))
        d2= datetime.datetime(int(b[0]),int(b[1]),int(b[2]))

        if d1<d2:
            Start_Date = StartDate.replace('-','')
            End_Date = EndDate.replace('-','')
            st = str(Satellite)
            products = api.query(footprint,
                             date=(Start_Date,End_Date),
                             platformname=st,
                             cloudcoverpercentage=(0, 30))

            for prod_id, j in products.items():
                props = j.copy()
                props["id"] = prod_id
                pro_id = prod_id
                ccp = props["cloudcoverpercentage"]
                begin_pos = props["beginposition"]
                fname = props["filename"]
                end_pos = props["endposition"]
                gendate= props["generationdate"]
                try:
                    database = Sentinel_Data(product_id=pro_id, fileName=fname, cloudCovPer=ccp, st_date=begin_pos, en_date=end_pos,Gen_date=gendate)
                    db.session.add(database)
                    db.session.commit()
                except:
                    print("Product Id already exist")
            if len(products)>0:
                return jsonify(products)
            else:
                return jsonify(error='Data not found')
        else:
            return jsonify(error='Ending date must be greater than Start date')

@app.route("/data/<id>", methods=["GET"])
def pro_details1(id):
        response = Sentinel_Data.query.filter_by(product_id=id).all()
        if (len(response)>=1):
            result1 = my_Data.dump(response)
            return make_response(jsonify(result1))
        else:
            return jsonify(error="Id not Found")

@app.route("/data/getdata/<id>", methods=['DELETE'])
def Deletedata(id):
    response1 = Sentinel_Data.query.filter_by(product_id=id).all()
    if (len(response1) >= 1):
        for items in response1:
            db.session.delete(items)
            db.session.commit()
        return 'Your data is deleted Sucessfully...'
    else:
        app.errorhandler()

if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0',port=12345)
