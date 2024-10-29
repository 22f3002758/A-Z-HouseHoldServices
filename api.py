from flask_restful import Resource,fields,marshal_with
from flask import request
from app import Services,db

services_field={
    "s_name":fields.String,
    "baseprice":fields.Integer
}

class CreateService(Resource):
    @marshal_with(services_field)
    def post(self):
        sn=request.json.get("sn")
        bp=request.json.get("bp")
        
        
        servicename=db.session.query(Services).filter_by(s_name=sn).first()
        print("hi")
        if servicename:
            return "Already Exist"
        else:
            add_ser=Services(s_name=sn,baseprice=bp)
            db.session.add(add_ser)
            db.session.commit()
            print("commited")
            return (add_ser,201)
def setup_routes(api):
    api.add_resource(CreateService, '/api/CreateService')    
    
# class ProviderApi(Resource):