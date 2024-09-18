from flask import Flask,request, render_template, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey,Nullable

app=Flask(__name__)# create constructor
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
db = SQLAlchemy(app) # connect app with sqlalchemy
app.app_context().push()# push it in the server

class Admin(db.Model):
    __tablename__='admin'

    admin_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    admin_email=db.Column(db.String,unique=True)
    admin_password=db.Column(db.String,unique=True)

class ServiceProvider(db.Model):
    __tablename__='serviceprovider'

    sp_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    sp_name=db.Column(db.String,unique=True)
    sp_address=db.Column(db.String)
    sp_email=db.Column(db.String,unique=True)
    sp_password=db.Column(db.String)
    sp_service=db.Column(db.String)
    sp_exp=db.Column(db.Integer)
    sp_phone=db.Column(db.String)
    sp_pincode=db.Column(db.String)
    # sp_camp_child=db.relationship('Campaign')
    # camp_request_sp=db.relationship('Request')  

class Customer(db.Model):
    __tablename__="customer" 

    c_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    c_name=db.Column(db.String,unique=True)
    c_address=db.Column(db.String)
    c_pincode=db.Column(db.String) 
    c_email=db.Column(db.String,unique=True)
    c_password=db.Column(db.String)
    c_phone=db.Column(db.String)   

class Services(db.Model):
    __tablename__="services"

    s_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    s_name=db.Column(db.String,unique=True)
    packages=db.relationship("Package", backref="service")

      
class Package(db.Model):
    __tablename__="package"

    p_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    p_name=db.Column(db.String,unique=True)
    p_price=db.Column(db.Integer)
    s_id=db.Column(db.Integer, db.ForeignKey("services.s_id"),nullable=False)


class Booking(db.Model) :
    __tablename__="booking"

    b_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    # s_id=db.Column(db.Integer, ForeignKey(services.s_id),nullable=False)
    sp_id=db.Column(db.Integer, db.ForeignKey("serviceprovider.sp_id"),nullable=False)
    c_id=db.Column(db.Integer, db.ForeignKey("customer.c_id"),nullable=False)
    p_id=db.Column(db.Integer, db.ForeignKey("package.p_id"),nullable=False)

@app.route("/", methods=["GET","POST"])
def home():
        
    return render_template("home.html")

@app.route ("/register", methods=["GET","POST"])

def register():
    if request.method=="GET" and request.args["utype"]=="customer":
        return render_template("/customer/register_customer.html")
    elif request.method=="POST" and request.args["utype"]=="customer":
        cname=request.form.get("c_name")
        caddress=request.form.get("c_address")
        cpincode=request.form.get("c_pincode")
        cemail=request.form.get("c_email")
        cpwd=request.form.get("c_pwd")
        cphone=request.form.get("c_phone")
        c=db.session.query(Customer).filter_by(c_email=cemail).first()
        if c:
            return redirect("/exist")
        else:
            cust=Customer(c_name=cname,c_address=caddress, c_pincode=cpincode,c_email=cemail,c_pwd=cpwd,c_phone=cphone)
            db.session.add(cust)
            db.session.commit    
            return render_template("login.html")
        

    elif request.method=="GET" and request.args["utype"]=="serviceprovider":
        return render_template("/ServiceProvider/register_service.html") 
    elif request.method=="POST" and request.args["utype"]=="service":
        spname=request.form.get("s_name")
        spaddress=request.form.get("s_address")
        sppincode=request.form.get("s_pincode")
        spemail=request.form.get("s_email")
        sppwd=request.form.get("s_pwd")  
        spexp=request.form.get("s_exp") 
        spphone=request.form.get("s_phone")
        s=db.session.query(ServiceProvider).filter_by(sp_email=spemail).first()
        if s:
            return redirect("/exist")
        else:
            sp=ServiceProvider(sp_name=spname,sp_address=spaddress, sp_pincode=sppincode,sp_email=spemail,sp_pwd=sppwd,sp_phone=spphone,sp_exp=spexp)
            db.session.add(sp)
            db.session.commit    
            return render_template("login.html")

if __name__=="__main__":
    app.run(debug=True)