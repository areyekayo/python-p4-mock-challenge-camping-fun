#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = [
            camper.to_dict(
                only=('id', 'name', 'age')
            ) 
            for camper in Camper.query.all()
        ]
        return make_response(jsonify(campers), 200)
    
    def post(self):
        data = request.get_json()
        try:
            camper = Camper(
                name=data['name'],
                age=data['age']
            )
            db.session.add(camper)
            db.session.commit()

            camper_dict = {
                'id': camper.id,
                'name': camper.name,
                'age': camper.age
            }
            return camper_dict, 201
        
        except Exception as e:
            db.session.rollback()
            errors_dict = {}
            message = str(e)
            errors_dict['error'] = [message]
            return {'errors': errors_dict}, 400
    
class CampersById(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            camper_dict = camper.to_dict(only=('id', 'name', 'age', 'signups'))
            return camper_dict, 200
        else:
            return {"error": "Camper not found"}, 404
        
    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            try: 
                data = request.get_json()

                for attr, value in data.items():
                    setattr(camper, attr, value)
                
                db.session.add(camper)
                db.session.commit()

                camper_dict = camper.to_dict(only=('id', 'name', 'age'))
                return camper_dict, 202
            
            except Exception:
                db.session.rollback()
                return {'errors': ["validation errors"]}, 400
        else:
            return {"error": "Camper not found"}, 404
        
class Activities(Resource):
    def get(self):
        activities = [
            activity.to_dict(
                only=('id', 'name', 'difficulty')
            ) for activity in Activity.query.all()
        ]
        return make_response(jsonify(activities), 200)
    
class ActivityById(Resource):
    def delete(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return {}, 204
        
        return {"error": "Activity not found"}, 404
    
class Signups(Resource):
    def post(self):
        data = request.get_json()
        try: 
            signup = Signup(
                camper_id=data['camper_id'],
                activity_id=data['activity_id'],
                time=data['time']
            )
            db.session.add(signup)
            db.session.commit()

            signup_dict = signup.to_dict(only=('id', 'camper_id', 'activity_id', 'time', 'activity', 'camper'))
            return signup_dict, 201
        
        except Exception:
            db.session.rollback()
            return {'errors': ["validation errors"]}, 400

api.add_resource(Campers, '/campers')
api.add_resource(CampersById, '/campers/<int:id>')
api.add_resource(Activities, '/activities')
api.add_resource(ActivityById, '/activities/<int:id>')
api.add_resource(Signups, '/signups')
                
if __name__ == '__main__':
    app.run(port=5555, debug=True)
