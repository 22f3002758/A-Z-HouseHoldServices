from flask_restful import API,Resource,fields,marshal_with
from flask import request
from app import Services,db

class CreateService(Resource):
    def post(self):
        sn=request.json.get("sn")
        bp=request.json.get("bp")
        
        
        servicename=db.session.query(Services).filter_by(s_name=sn).first()
        if servicename:
            return "Already Exist"
        else:
            add_ser=Services(s_name=sn,baseprice=bp)
            db.session.add(add_ser)
            db.session.commit()
            return 201