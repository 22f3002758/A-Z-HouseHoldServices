from flask import Flask,request, render_template, redirect,url_for,flash
from flask_restful import Api,Resource,fields,marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey,Nullable
from flask_login import LoginManager, login_user, logout_user, login_required, current_user,UserMixin
import datetime
import requests
import seaborn as sns
import matplotlib
matplotlib.use('agg') # to remove interactive backend
import matplotlib.pyplot as plt
import fitz
import math


app=Flask(__name__)# create constructor
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
app.config['SECRET_KEY']="mysecretkey" # secure sessions and cookie
db=SQLAlchemy(app) # connect app database with sqlalchemy, it is ORM allows you to interact with the database using Python objects instead of raw SQL queries.
api=Api(app)
login_manager=LoginManager(app) #Flask-Login provides user session management, helping you handle login and logout functionality.

app.app_context().push() #This pushes the application context to the stack. 
#The context is necessary to access current app-related objects, such as configuration and database, outside of request handling.
#  It's often used during initialization scripts or in interactive Python sessions.
################################################################################################

class ServiceApi(Resource):
    
    def post(self):
        sn=request.json.get("sn")
        bp=request.json.get("bp")
        
        
        servicename=db.session.query(Services).filter_by(s_name=sn).first()
        if servicename:
            return {"message": "Service already exists"}, 409
        else:
            add_ser=Services(s_name=sn,baseprice=bp)
            db.session.add(add_ser)
            db.session.commit()
            return {"message": "Service Created."}, 201
        
    
    def put(self):
        sn=request.json.get("sn")
        bp=request.json.get("bp")
        sid=request.json.get("s_id")
        up_ser=db.session.query(Services).filter_by(s_id=sid).first()
        if up_ser:
            if sn:
                up_ser.s_name=sn
            if bp:    
                up_ser.baseprice=bp
            db.session.commit()
            return {"message": "Service Updated."},200
        
        else:
            return {"message": "Service not found."}, 204

    def delete(self):
        sid=request.json.get("s_id")   
        servicename=db.session.query(Services).filter_by(s_id=sid).first()
        if servicename:
            db.session.delete(servicename)
            db.session.commit()
            return {"message": "Service Deleted"}, 200
        else:
            return {"message": "Service does not exist"},204
    

class BookApi(Resource):
    def post(self):
        spid=request.json.get("spid")
        pid=request.json.get("pid")
        cid=request.json.get('cid')
        rdate = request.json.get("rdate")
        rtime = request.json.get("rtime")
        raddress = request.json.get("raddress")
        rcity = request.json.get("rcity")
        rstatus = request.json.get('rstatus')
        R= Request(sp_id=spid,p_id=pid,c_id=cid,r_date=rdate, r_time=rtime,r_address=raddress,r_city=rcity,r_status=rstatus,r_rating=0)
        db.session.add(R)
        db.session.commit()
        return {"message":"Booking request created"}, 200
    
    def put(self):
        if request.args.get('change')=='edit':
            rid=request.json.get("rid")
            edate=request.json.get("edate")
            etime=request.json.get("etime")
            edit_req=db.session.query(Request).filter_by(r_id=rid).first()
            edit_req.r_date=edate
            edit_req.r_time=etime
            db.session.commit()
            return {'message': "Booking updated"}, 200
        elif request.json.get('r_status')=='Closed':
            rid=request.json.get("rid")
            close_req=db.session.query(Request).filter_by(r_id=rid).first()
            close_req.r_status="Closed"
            db.session.commit()
            return {"message":"Booking request closed"}, 200
        elif request.json.get('r_status')=='Cancelled':
            rid=request.json.get("rid")
            cancel_req=db.session.query(Request).filter_by(r_id=rid).first()
            cancel_req.r_status="Cancelled"  
            db.session.commit() 
            return {"message":"Booking request cancelled"}, 200
        elif request.json.get('r_status')=='Accepted': 
            rid=request.json.get("rid")
            close_req=db.session.query(Request).filter_by(r_id=rid).first()
            close_req.r_status="Accepted"
            db.session.commit()
            return {"message":"Booking request accepted"}, 200
        elif request.json.get('r_status')=='Rejected': 
            rid=request.json.get("rid")
            close_req=db.session.query(Request).filter_by(r_id=rid).first()
            close_req.r_status="Rejected"
            db.session.commit()
            return {"message":"Booking request rejected"}, 200
        elif request.json.get('r_status')=='Finished': 
            rid=request.json.get("rid")
            close_req=db.session.query(Request).filter_by(r_id=rid).first()
            close_req.r_status="Finished"
            db.session.commit()
            return {"message":"Booking request Finished"}, 200
        
class FlagApi(Resource):
    def put(self):
        if request.json.get("sp_status")=='Flagged':
            spid=request.json.get("spid")
            sp=db.session.query(ServiceProvider).filter_by(sp_id=spid).first()
            sp.sp_status="Flagged"
            db.session.commit()
            return {"message":f'{sp.sp_name} has been Flagged'}, 200
        elif request.json.get("sp_status")=='UnFlagged':
            spid=request.json.get("spid")
            sp=db.session.query(ServiceProvider).filter_by(sp_id=spid).first()
            sp.sp_status="Active"
            db.session.commit()
            return {"message":f'{sp.sp_name} has been Unflagged'}, 200
        if request.json.get("c_status")=='Flagged':
            cid=request.json.get("cid")
            c=db.session.query(Customer).filter_by(c_id=cid).first()
            c.c_status="Flagged"
            db.session.commit()
            return {"message":f'{c.c_name} has been Flagged'}, 200
        elif request.json.get("c_status")=='UnFlagged':
            cid=request.json.get("cid")
            c=db.session.query(Customer).filter_by(c_id=cid).first()
            c.c_status="Active"
            db.session.commit()
            return {"message":f'{c.c_name} has been Unflagged'}, 200
        
class PackageApi(Resource):
    def put(self):
        pid=request.json.get('pid')
        pn=request.json.get('pn')
        pd=request.json.get('pd')
        pp=request.json.get('pp')
        edit_pack=db.session.query(Package).filter_by(p_id=pid).first()
        if pn:
            edit_pack.p_name=pn
        if pd:
            edit_pack.p_description=pd
        if pp:
            edit_pack.p_price=pp
        db.session.commit()   
        return {"message":"Package Updated"}, 200

    def post(self):
        pn=request.json.get('pn')
        pd=request.json.get('pd')
        pp=request.json.get('pp')
        spid=request.json.get('spid')
        sid=request.json.get('sid')
        
        create_pack=Package(p_price=pp,p_name=pn,p_description=pd,sp_id=spid,s_id=sid,p_rating=0)
        db.session.add(create_pack)
        db.session.commit()
        return {"message":"Package Created"}, 200

class AdminApi(Resource):
    def put(self):
        adname=request.json.get("adname")
        ademail=request.json.get("ademail")
        adpwd=request.json.get("adpwd")
        ad=db.session.query(Admin).first()
        if adname:
            ad.admin_name=adname
        if ademail:
            ad.admin_email=ademail
        if adpwd:
            ad.admin_password=adpwd
        db.session.commit()  
        return {"message" : "Profile Updated"}, 200 

     
class CustomerApi(Resource):
    def put(self):
        cid=request.json.get("cid")
        cn=request.json.get("cn")
        ce=request.json.get("ce")
        cc=request.json.get("cc")
        cp=request.json.get("cp")
        ca=request.json.get("ca")
        cpwd=request.json.get("cpwd")
        cu=db.session.query(Customer).filter_by(c_id=cid).first()
        if cn:
            cu.c_name=cn
        if ce:
            cu.c_email=ce
        if cp:
            cu.c_phone=cp
        if ca:
            cu.c_address=ca
        if cpwd:
            cu.c_password=cpwd
        if cc:
            cu.c_city=cc
        db.session.commit()  
        return {"message" : "Profile Updated"}, 200 
    
    def post(self):
        cname=request.json.get("cname")
        caddress=request.json.get("caddress")
        ccity=request.json.get("ccity")
        cemail=request.json.get("cemail")
        cpwd=request.json.get("cpwd")
        cphone=request.json.get("cphone")
        c=db.session.query(Customer).filter_by(c_email=cemail).first()

        if c:
            return {"message" : "User already Exist"}, 409
        else:
            cust=Customer(c_name=cname,c_address=caddress, c_city=ccity,c_email=cemail,c_password=cpwd,c_phone=cphone,c_status='Active')
            db.session.add(cust)
            db.session.commit() 
            return {"message" : "Profile Created"}, 200
    
    
class ServiceProviderApi(Resource):
    def post(self):
        spname=request.form.get("spname")
        spaddress=request.form.get("spaddress")
        spcity=request.form.get("spcity")
        spemail=request.form.get("spemail")
        sppwd=request.form.get("sppwd")  
        spexp=request.form.get("spexp") 
        sername=request.form.get("sername")
        spphone=request.form.get("spphone")
        sresume=request.files.get("sresume")
        sp=db.session.query(ServiceProvider).filter_by(sp_email=spemail).first()
        if sp:
            return {"message" : "User already Exist"}, 409
        else:
            pdf=fitz.open(stream=sresume.read(),filetype="pdf")
            image=pdf.load_page(0).get_pixmap()
            image.save(f'./static/sp/Resume/{spemail}.png')
            sp=ServiceProvider(sp_name=spname,sp_address=spaddress, sp_city=spcity,sp_email=spemail,
                                sp_password=sppwd,sp_phone=spphone,sp_exp=spexp,sp_status="Requested",
                                sp_rating=0,sp_rfile=f'/static/sp/Resume/{spemail}.png',sp_servicename=sername)
            db.session.add(sp)
            db.session.commit() 
            return {"message" : "Profile Created"}, 200
        
    def put(self):
        spid=request.json.get("spid")
        spname=request.json.get("spname")
        spaddress=request.json.get("spaddress")
        spcity=request.json.get("spcity")
        spemail=request.json.get("spemail")
        sppwd=request.json.get("sppwd")   
        spphone=request.json.get("spphone")
        
        sp=db.session.query(ServiceProvider).filter_by(sp_id=spid).first()
        
        if spname:
            sp.sp_name=spname
        if spaddress:
            sp.sp_address=spaddress
        if spcity:
            sp.sp_city=spcity
        if spphone:
            sp.sp_phone=spphone
        if sppwd:
            sp.sp_password=sppwd
        if spemail:
            sp.sp_email=spemail
        db.session.commit()  
        return {"message" : "Profile Updated"}, 200  

class StatisticsApi(Resource):
    def get(self,u_type):
        if u_type=='admin':
            ser=db.session.query(Services).filter_by(s_name='Home Cleaning').first()
            L=[0,0,0]
            for i in ser.packages:
                for j in i.req:
                    if j.r_status=='Accepted':
                        L[0]+=1
                    elif j.r_status=='Closed':
                        L[1]+=1    
                    elif j.r_status=='Requested':
                        L[2]+=1
                        
            Xcat = ["Accepted", "Closed", "Requested"]
            
            colors = sns.color_palette("pastel", len(Xcat))  
            fig, ax = plt.subplots()
            bars = ax.bar(Xcat, L, color=colors)
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height + 0.1, f'{height}', ha='center', va='bottom')

            labels = [(label, colors[i]) for i, label in enumerate(Xcat)]

            if labels:
                for i, (label, color) in enumerate(labels):
                    fig.text(0.5 + (i - len(labels) / 2) * 0.15, -0.1, label, 
                            ha='center', va='center', fontsize=10, style='italic', 
                            bbox=dict(facecolor=color, edgecolor='none', boxstyle='round,pad=0.3'))
            ax.set_title('Service Requests Distribution')
            ax.set_ylabel('Number of Requests')
            plt.savefig("./static/ad/bar1.png", bbox_inches='tight')
            plt.clf()
            allser=db.session.query(Services).all()
            d={}
            for ser in allser:
                d[ser.s_name]=0
                for pack in ser.packages:
                    for req in pack.req:
                        if req.r_status=='Closed':
                            d[ser.s_name]+=1
            palette = sns.color_palette("pastel", len(d))
            labels = [key for key, value in d.items() if value > 0]
            sizes = [value for value in d.values() if value > 0]
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=palette[:len(sizes)])
            plt.axis('equal')  
            plt.title('Services wise distribution')
            zero_labels = [label for label, size in d.items() if size == 0]
            zero_colors = palette[len(sizes):len(sizes) + len(zero_labels)]
            if zero_labels:
                for i, (label, color) in enumerate(zip(zero_labels, zero_colors)):
                    fig.text(0.5 + (i - len(zero_labels) / 2) * 0.15, -0.05, label, 
                            ha='center', va='center', fontsize=10, style='italic', 
                            bbox=dict(facecolor=color, edgecolor='none', boxstyle='round,pad=0.3'))
            plt.savefig('./static/ad/pie1.png', bbox_inches='tight')
            plt.clf()

        elif u_type=='customer':
            cid=request.json.get('cid')
            req=db.session.query(Request).filter_by(c_id=cid).all()
            f=[0,0,0]
            
            for req in req:
                # d=req.r_date.split("-")
                if req.r_status=="Accepted":
                    f[0]+=1
                elif req.r_status=="Rejected":
                    f[1]+=1
                elif req.r_status=="Closed":
                    f[2]+=1       
            X=["Accepted","Rejected","Closed"]
        
            colors = sns.color_palette("pastel", len(X))

            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x=X, y=f, palette=colors, ax=ax)

            for index, value in enumerate(f):
                ax.text(index, value + 0.1, str(value), ha='center', va='bottom')

            ax.set_xlabel("Status")
            ax.set_ylabel("Count")
            labels = [(label, colors[i]) for i, label in enumerate(X)]
            if labels:
                for i, (label, color) in enumerate(labels):
                    fig.text(0.5 + (i - len(labels) / 2) * 0.15, +0, label,
                            ha='center', va='center', fontsize=10, style='italic',
                            bbox=dict(facecolor=color, edgecolor='none'))
            plt.savefig("./static/cus/bar1.png", bbox_inches='tight')
            plt.clf()

        elif u_type=='serviceprovider':
            spid=request.json.get('spid')
            req=db.session.query(Request).filter_by(sp_id=spid).all()
            f=[0,0,0]
            
        
            for r in req:
                # d=req.r_date.split("-")
                if r.r_status=="Accepted":
                    f[0]+=1
                elif r.r_status=="Rejected":
                    f[1]+=1
                elif r.r_status=="Closed":
                    f[2]+=1       
            X=["Accepted","Rejected","Closed"]
        
            colors = sns.color_palette("pastel", len(X))

            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x=X, y=f, palette=colors, ax=ax)

            for index, value in enumerate(f):
                ax.text(index, value + 0.0, str(value), ha='center', va='bottom')

            ax.set_xlabel("Status")
            ax.set_ylabel("Count")
            labels = [(label, colors[i]) for i, label in enumerate(X)]
            if labels:
                for i, (label, color) in enumerate(labels):
                    fig.text(0.5 + (i - len(labels) / 2) * 0.15, +0, label,
                            ha='center', va='center', fontsize=10, style='italic',
                            bbox=dict(facecolor=color, edgecolor='none'))
            plt.savefig("./static/sp/bar1.png", bbox_inches='tight')
            plt.clf()

    def post(self,u_type):
        if u_type=='admin':
            sn=request.json.get('sname')
            ser=db.session.query(Services).filter_by(s_name=sn).first()
            L=[0,0,0]
            for i in ser.packages:
                for j in i.req:
                    if j.r_status=='Accepted':
                        L[0]+=1
                    elif j.r_status=='Closed':
                        L[1]+=1    
                    elif j.r_status=='Requested':
                        L[2]+=1
                        
            Xcat = ["Accepted", "Closed", "Requested"]
            
            colors = sns.color_palette("pastel", len(Xcat))  
            fig, ax = plt.subplots()
            bars = ax.bar(Xcat, L, color=colors)
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height - 0.1, f'{height}', ha='center', va='bottom')

            labels = [(label, colors[i]) for i, label in enumerate(Xcat)]

            if labels:
                for i, (label, color) in enumerate(labels):
                    fig.text(0.5 + (i - len(labels) / 2) * 0.15, -0.1, label, 
                            ha='center', va='center', fontsize=10, style='italic', 
                            bbox=dict(facecolor=color, edgecolor='none'))
            ax.set_title(f'{sn} Request Summary',pad=20)
            ax.set_ylabel('Number of Requests')
            plt.savefig("./static/ad/bar1.png", bbox_inches='tight')
            plt.clf()

api.add_resource(ServiceApi, '/api/service/create','/api/service/update','/api/service/delete')
api.add_resource(BookApi,'/api/book','/api/book/edit')
api.add_resource(FlagApi,'/api/flag')
api.add_resource(PackageApi,'/api/package/create','/api/package')
api.add_resource(AdminApi,'/api/admin/update')
api.add_resource(CustomerApi,'/api/customer/register','/api/customer/update')
api.add_resource(ServiceProviderApi,'/api/serviceprovider/register','/api/serviceprovider/update')
api.add_resource(StatisticsApi,'/api/stats/<u_type>')

###############################################################################################
class Admin(db.Model,UserMixin):
    __tablename__='admin'

    admin_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    admin_name=db.Column(db.String)
    admin_email=db.Column(db.String,unique=True)
    admin_password=db.Column(db.String,unique=True)

    def get_id(self):
        return f'a-{self.admin_id}'
    
class ServiceProvider(db.Model,UserMixin):
    __tablename__='serviceprovider'

    sp_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    sp_name=db.Column(db.String,unique=True)
    sp_address=db.Column(db.String)
    sp_email=db.Column(db.String,unique=True)
    sp_password=db.Column(db.String)
    sp_exp=db.Column(db.Integer)
    sp_phone=db.Column(db.String)
    sp_city=db.Column(db.String)
    sp_rating=db.Column(db.Integer)
    sp_status=db.Column(db.String)
    sp_rfile=db.Column(db.String)
    sp_servicename=db.Column(db.String,db.ForeignKey("services.s_name"))
    mypackages=db.relationship("Package", backref="servprovider",cascade="all, delete-orphan")
    receive_request=db.relationship("Request",backref="servprovider",cascade="all, delete-orphan")
    

    # sp_camp_child=db.relationship('Campaign')
    # camp_request_sp=db.relationship('Request')  

    
    def get_id(self):
        return f'sp-{self.sp_id}'

class Customer(db.Model,UserMixin):
    __tablename__="customer" 

    c_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    c_name=db.Column(db.String,unique=True)
    c_address=db.Column(db.String)
    c_city=db.Column(db.String) 
    c_email=db.Column(db.String,unique=True)
    c_password=db.Column(db.String)
    c_phone=db.Column(db.String) 
    c_status=db.Column(db.String)
    Sent_Request=db.relationship("Request",backref="cust")
    
    def get_id(self):
       return f'c-{self.c_id}'  

class Services(db.Model):
    __tablename__="services"

    s_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    s_name=db.Column(db.String,unique=True)
    baseprice=db.Column(db.Integer)
    packages=db.relationship("Package", backref="service")
    Sproviders=db.relationship("ServiceProvider",backref="service", cascade="all, delete-orphan")


    

      
class Package(db.Model):
    __tablename__="package"

    p_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    p_name=db.Column(db.String)
    p_price=db.Column(db.Integer)
    p_description=db.Column(db.String)
    p_rating=db.Column(db.Integer)
    s_id=db.Column(db.Integer, db.ForeignKey("services.s_id"),nullable=False)
    sp_id=db.Column(db.Integer, db.ForeignKey("serviceprovider.sp_id"),nullable=False)
    req=db.relationship("Request",backref="pack")


class Request(db.Model):
    __tablename__="request"

    r_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    sp_id=db.Column(db.Integer, db.ForeignKey("serviceprovider.sp_id"),nullable=False)
    c_id=db.Column(db.Integer, db.ForeignKey("customer.c_id"),nullable=False)
    p_id=db.Column(db.Integer, db.ForeignKey("package.p_id"),nullable=False)
    r_date=db.Column(db.String)
    r_time=db.Column(db.String)
    r_address=db.Column(db.String)
    r_city=db.Column(db.String)
    r_status=db.Column(db.String)
    r_rating=db.Column(db.Integer)
   

##########################################################################################
@login_manager.user_loader
def load_user(user_id):
    utype,id=user_id.split("-")
    if utype=="c":
        return db.session.query(Customer).filter_by(c_id=id).first()
    elif utype=='sp':
        return db.session.query(ServiceProvider).filter_by(sp_id=id).first()
    else:
        return db.session.query(Admin).filter_by(admin_id=id).first()


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
        ccity=request.form.get("c_city")
        cemail=request.form.get("c_email")
        cpwd=request.form.get("c_pwd")
        cphone=request.form.get("c_phone")
        response=requests.post("http://127.0.0.1:5000/api/customer/register",json={"cname":cname,'caddress': caddress,'ccity':ccity,'cemail':cemail,"cpwd":cpwd,"cphone":cphone})
        if response.status_code==200:
            return redirect("/login")
        else:
            flash(response.json()['message'])
            return redirect("/register?utype=customer")       

    elif request.method=="GET" and request.args["utype"]=="serviceprovider":
        serv=db.session.query(Services).all()
        
        return render_template("/ServiceProvider/register_service.html",services=serv) 
    elif request.method=="POST" and request.args["utype"]=="serviceprovider":
        spname=request.form.get("sp_name")
        spaddress=request.form.get("sp_address")
        spcity=request.form.get("sp_city")
        spemail=request.form.get("sp_email")
        sppwd=request.form.get("sp_password")  
        spexp=request.form.get("sp_exp") 
        sername=request.form.get("sp_service")
        spphone=request.form.get("sp_phone")
        sresume=request.files["resume"]
        response=requests.post("http://127.0.0.1:5000/api/serviceprovider/register",data={"spname":spname,'spaddress': spaddress,'spcity':spcity,'spemail':spemail,"sppwd":sppwd,"spexp":spexp,"sername":sername,"spphone":spphone},files={"sresume": (sresume.filename, sresume, sresume.content_type)})
        if response.status_code==200:
            return redirect("/login")
        else:
            flash(response.data()['message'])
            return redirect("/register?utype=serviceprovider")

        
@app.route("/profile-update", methods=["GET","POST"])
@login_required
def update():
    if request.method=="POST" and request.args.get("utype")=="customer":
        cu=current_user
        cn=request.form.get("cname")
        ce=request.form.get("cemail")
        cc=request.form.get("ccity")
        cp=request.form.get("phone")
        ca=request.form.get("cadd")
        cpwd=request.form.get("cpwd")
        
        response=requests.put("http://127.0.0.1:5000/api/customer/update",json={"cp":cp,"cn":cn,'ce': ce,'cc':cc,'cp':ca,'cpwd':cpwd,'cid':cu.c_id})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/customer/Dashboard")
        else:
            return "something went wrong"
    elif request.method=="POST" and request.args.get("utype")=="serviceprovider":  
        spid=current_user.sp_id
        spname=request.form.get("sp_name")
        spaddress=request.form.get("sp_address")
        spcity=request.form.get("sp_city")
        spemail=request.form.get("sp_email")
        sppwd=request.form.get("sp_pwd")  

        spphone=request.form.get("sp_phone")
        response=requests.put("http://127.0.0.1:5000/api/serviceprovider/update",json={"spid":spid,'spname': spname,'spaddress':spaddress,'spcity':spcity,'spemail':spemail,'sppwd':sppwd,"spphone":spphone})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/serviceprovider/dashboard")
        else:
            return "something went wrong"  
    elif request.method=="POST" and request.args.get("utype")=="admin":
        cu=current_user
        adname=request.form.get("adname")
        ademail=request.form.get("ademail")
        adpwd=request.form.get("adpwd")
        response=requests.put("http://127.0.0.1:5000/api/admin/update",json={"adname":adname,'ademail': ademail,'adpwd':adpwd})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/admin/dashboard")
        else:
            return "something went wrong"  



@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        email=request.form.get("Email")
        pwd=request.form.get("Password")
        c=db.session.query(Customer).filter_by(c_email=email).first()
        sp=db.session.query(ServiceProvider).filter_by(sp_email=email).first()
        ad=db.session.query(Admin).filter_by(admin_email=email).first()
        if c and c.c_password==pwd:
            login_user(c)
            return redirect("/customer/Dashboard")
        elif sp and sp.sp_password==pwd:
            login_user(sp)
            return redirect("/serviceprovider/dashboard")
        elif ad and ad.admin_password==pwd:
            login_user(ad)
            return redirect("/admin/dashboard")
        else:
            return render_template("notexist.html")


@app.route("/customer/Dashboard",methods=["GET","POST"])
@login_required
def Dashboard():
    if request.method=="GET":
        s=db.session.query(Services).all()
        
        serv=[]
        for ser in s:
            serv.append(ser.s_name)

        req=db.session.query(Request).filter_by(c_id=current_user.c_id).all()    
        return render_template("/Customer/CustomerDashboard.html",servname=serv,requests=req,cu=current_user)
    
@app.route("/customer/book", methods=["GET","POST"])
@login_required
def book():
    if request.method=="POST" and "edit" in request.args:
        rid=request.args.get("rid")
        edate=request.form.get("Date")
        etime=request.form.get("Time")
        response=requests.put("http://127.0.0.1:5000/api/book/edit?change=edit",json={"rid":rid,"edate":edate,"etime":etime})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/customer/Dashboard")
        else:
            return "something went wrong"
        
    elif request.method=="POST" and "cancel" in request.args:
        rid=request.args.get("rid")
        response=requests.put("http://127.0.0.1:5000/api/book/edit",json={"rid":rid,'r_status':"Cancelled"})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/customer/Dashboard")
        else:
            return "something went wrong"
        
    elif request.method=="POST" and "close" in request.args:
        rid=request.args.get("rid")
        response=requests.put("http://127.0.0.1:5000/api/book/edit",json={"rid":rid,'r_status':"Closed"})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/customer/Dashboard")
        else:
            return "something went wrong"
        
    elif request.method == "POST":
        spid=request.args.get("spid")
        pid=request.args.get("pid")
        cid=current_user.c_id
        rdate = request.form.get("Date")
        rtime = request.form.get("Time")
        raddress = request.form.get("c_add")
        rcity = request.form.get("c_city")
        rstatus = "Requested"
        response=requests.post("http://127.0.0.1:5000/api/book",json={"spid":spid,"pid":pid,"cid":cid,"rdate":rdate,"rtime":rtime,"rcity":rcity,"rstatus":rstatus})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/customer/Dashboard")
        else:
            return "something went wrong"
        
    
@app.route("/rating",methods=["GET","POST"])
@login_required
def rating():
    if request.method=="POST"  :
        rate=request.form.get("rate")
        pack=request.args.get("pack")
        rid=request.args.get("rid")
        p=db.session.query(Package).filter_by(p_id=pack).first()
        req=db.session.query(Request).filter_by(r_id=rid).first()
        p.p_rating=rate
        req.r_rating=rate
        req.r_status="Closed"
        db.session.commit()
        return redirect("/customer/Dashboard")

    

@app.route("/customer/search",methods=["GET","POST"])
@login_required
def search():
    if request.method=="GET" and "sname" in request.args:
        s=request.args.get("sname")
        ser=db.session.query(Services).filter_by(s_name=s).first()
        pack = db.session.query(Package).filter_by(s_id=ser.s_id).order_by(Package.p_rating.desc()).all()
        Servis=db.session.query(Services).all()
        return render_template("/Customer/custsearch.html",package=pack,Services=Servis,cu=current_user,show='post')
    
    elif request.method=="GET" :
        Servis=db.session.query(Services).all()
        return render_template("/Customer/custsearch.html",Services=Servis,cu=current_user)
    
    elif request.method=="POST":    
        ser=request.form.get("service")
        citi=request.form.get("city")
        Servis=db.session.query(Services).all()
        Servisprovider=db.session.query(ServiceProvider).filter_by(sp_servicename=ser,sp_city=citi).all()
        pack=[]
        for sp in Servisprovider:
            for p in sp.mypackages:
                pack.append(p)   
                     
        return render_template("/Customer/custsearch.html",package=pack,Services=Servis,cu=current_user,show='post')
        


@app.route("/customer/stats",methods=["GET","POST"])  
@login_required
def cus_stats():
    if request.method=="GET":
        cid=current_user.c_id
        response=requests.get('http://127.0.0.1:5000/api/stats/customer',json={'cid':cid})
        if response.status_code==200:
            return render_template("/customer/cus_stats.html",cu=current_user)
        else:
            return "Something went wrong"
    
        
    
@app.route("/serviceprovider/dashboard", methods=["GET","POST"])
@login_required
def SPDashboard():
    if request.method=="GET" and "accept" in request.args:
        rid=request.args.get("rid")
        response=requests.put("http://127.0.0.1:5000/api/book/edit",json={"rid":rid,'r_status': 'Accepted'})
        if response.status_code==200:
            return redirect("/serviceprovider/dashboard")
        else:
            return "something went wrong"

    elif request.method=="POST" and "reject" in request.args:
        rid=request.args.get("rid")
        response=requests.put("http://127.0.0.1:5000/api/book/edit",json={"rid":rid,'r_status': 'Rejected'})
        if response.status_code==200:
            return redirect("/serviceprovider/dashboard")
        else:
            return "something went wrong"
        
    elif request.method=="GET" and 'close' in request.args:
        rid=request.args.get("rid")
        response=requests.put("http://127.0.0.1:5000/api/book/edit",json={"rid":rid,'r_status': 'Finished'})
        if response.status_code==200:
            return redirect("/serviceprovider/dashboard")
        else:
            return "something went wrong"
        
    elif request.method=="GET":
        d=datetime.date.today()
        cd = d.strftime("%d-%m-%Y")
        r=db.session.query(Request).filter_by(sp_id=current_user.sp_id,r_date=cd,r_status="Accepted").all()
        Opser = db.session.query(Request).filter_by(sp_id=current_user.sp_id).filter(Request.r_status.in_(["Accepted", "Finished"])).all()
        reqser=db.session.query(Request).filter_by(sp_id=current_user.sp_id,r_status="Requested").all()
        closeser=db.session.query(Request).filter(Request.sp_id==current_user.sp_id,Request.r_status.in_(["Closed", "Cancelled"])).all()
        mypack=current_user.mypackages
        if mypack:
            rate=0
            for p in mypack:
                rate+=p.p_rating
            rating = math.ceil(rate / len(mypack))
        else:
            rating=0   
        current_user.sp_rating=rating
        db.session.commit()
        return render_template("/ServiceProvider/serviceprovider.html",cu=current_user,
                               rating=int(current_user.sp_rating),todays_requests=r,open_services=Opser,requested_services=reqser,closed_services=closeser)



@app.route("/serviceprovider/create",methods=["GET","POST"])
@login_required
def create_pack():
    if request.method=="GET":
        P=db.session.query(Package).filter_by(sp_id=current_user.sp_id).all()
        return render_template("/ServiceProvider/create_package.html",mypackage=P,cu=current_user)
    elif request.method=="POST" and "edit" in request.args:
        pid=request.args.get("pid")
        pn=request.form.get("pname")
        pd=request.form.get("pdesc")
        pp=request.form.get("pprice")
        response=requests.put("http://127.0.0.1:5000/api/package",json={"pid":pid,'pn': pn,'pd':pd,'pp':pp})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/serviceprovider/dashboard")
        else:
            return "something went wrong"
        
    elif request.method=="POST" and "create" in request.args:
        pn=request.form.get("pname")
        pd=request.form.get("pdesc")
        pp=request.form.get("pprice")
        response=requests.post("http://127.0.0.1:5000/api/package/create",json={'pn': pn,'pd':pd,'pp':pp,'spid':current_user.sp_id,'sid':current_user.service.s_id})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/serviceprovider/dashboard")
        else:
            return "something went wrong"
        

    
@app.route("/serviceprovider/stats",methods=["GET","POST"])  
@login_required
def stats():
    if request.method=="GET":
        spid=current_user.sp_id
        response=requests.get('http://127.0.0.1:5000/api/stats/serviceprovider',json={'spid':spid})
        if response.status_code==200:
            return render_template("/ServiceProvider/sp_stats.html",cu=current_user)
        else:
            return "Something went wrong"

    
        
@app.route("/admin/dashboard/",methods=["GET","POST"]) 
@login_required
def dashboard():
    
    if request.method=="GET" and request.args.get('target')=='Accept' :
        spid=request.args.get("spid")
        sp=db.session.query(ServiceProvider).filter_by(sp_id=spid).first()
        sp.sp_status="Active"
        db.session.commit()
        return redirect("/admin/dashboard/")
    elif request.method=="POST" and request.args.get('target')=='Reject':
        spid=request.args.get("spid")
        sp=db.session.query(ServiceProvider).filter_by(sp_id=spid).first()
        sp.sp_status="Rejected"
        db.session.commit()
        return redirect("/admin/dashboard/")
    elif request.method=="GET":
        ser=db.session.query(Services).all()
        act_sp=db.session.query(ServiceProvider).filter_by(sp_status="Active").all()
        req_sp=db.session.query(ServiceProvider).filter_by(sp_status="Requested").all()
        flag_sp=db.session.query(ServiceProvider).filter_by(sp_status="Flagged").all()
        act_c=db.session.query(Customer).filter_by(c_status="Active").all()
        flag_c=db.session.query(Customer).filter_by(c_status="Flagged").all()
        return render_template("/admin/Admin_dashboard.html",Services=ser,active=act_sp,requested=req_sp,flagged=flag_sp,cu=current_user,c_active=act_c,c_flag=flag_c)
    

@app.route("/admin/search" , methods=["GET", "POST"])  
@login_required
def ad_search():
    if request.method=="GET": 
        return render_template("/admin/adminsearch.html",cu=current_user)
    elif request.method=="POST":
        utype=request.form.get("utype")
        if utype=="customer":
            name=request.form.get("name")
            searchname=f'%{name}%'
            result=db.session.query(Customer).filter(Customer.c_name.ilike(searchname)).all()
        else:
            name=request.form.get("name")    
            searchname=f'%{name}%'
            result=db.session.query(ServiceProvider).filter(ServiceProvider.sp_name.ilike(searchname)).all()
        return render_template("/admin/adminsearch.html",cu=current_user,results=result,show='POST',utype=utype)
    

@app.route("/flag",methods=["GET","POST"])
@login_required
def flag():
    if request.method=="POST" and request.args["target"]=="sp" and request.args["action"]=="flag":
        spid=request.args.get("spid")
        response=requests.put("http://127.0.0.1:5000/api/flag",json={"spid":spid,'sp_status': 'Flagged'})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/admin/dashboard")
        else:
            return "something went wrong"

    elif request.method=="POST" and request.args["target"]=="sp" and request.args["action"]=="unflag":
        spid=request.args.get("spid")
        response=requests.put("http://127.0.0.1:5000/api/flag",json={"spid":spid,'sp_status': 'UnFlagged'})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/admin/dashboard")
        else:
            return "something went wrong"

    elif request.method=="POST" and request.args["target"]=="c" and request.args["action"]=="flag":
        cid=request.args.get("cid")
        response=requests.put("http://127.0.0.1:5000/api/flag",json={"cid":cid,'c_status': 'Flagged'})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/admin/dashboard")
        else:
            return "something went wrong"
    elif request.method=="POST" and request.args["target"]=="c" and request.args["action"]=="unflag" :
        cid=request.args.get("cid")
        response=requests.put("http://127.0.0.1:5000/api/flag",json={"cid":cid,'c_status': 'UnFlagged'})
        if response.status_code==200:
            flash(response.json()["message"])
            return redirect("/admin/dashboard")
        else:
            return "something went wrong"
        

@app.route("/admin/stats",methods=["GET","POST"]) 
@login_required 
def ad_stats():
    if request.method=="GET":
        cu=current_user 
        response=requests.get("http://127.0.0.1:5000/api/stats/admin")
        if response.status_code==200:
            ser=db.session.query(Services).all()
            return render_template("/admin/ad_stats.html",cu=cu,services=ser)   
        else:
            return "Something went wrong"
    elif request.method=="POST":
        cu=current_user 
        sn=request.form.get("sname")
        response=requests.post("http://127.0.0.1:5000/api/stats/admin",json={"sname":sn})
        if response.status_code==200:
            ser=db.session.query(Services).all()
            return render_template("/admin/ad_stats.html",cu=cu,services=ser)   
        else:
            return "Something went wrong"

    
@app.route("/service" , methods=["GET","POST"])
@login_required
def service():
    if request.method=="POST" and request.args['target']=='ns':
        sn=request.form.get("servicename")
        bp=request.form.get("baseprice")
        response=requests.post("http://127.0.0.1:5000/api/service/create",json={"sn":sn,"bp":bp})
        if response.status_code==201:
            return redirect("/admin/dashboard/")
        else:
            flash("service already exist")
            return redirect("/admin/dashboard/")
    elif request.method=="POST" and request.args['target']=='edit':
        sid=request.args.get("sid")
        sn=request.form.get("servicename")
        bp=request.form.get("baseprice")
        response=requests.put("http://127.0.0.1:5000/api/service/update",json={"sn":sn,"bp":bp,"s_id":sid})
        if response.status_code==200:
            flash("service updated")
            return redirect("/admin/dashboard/")
        else:
            flash("Error in update. Try again")
            return redirect("/admin/dashboard/")
    elif request.method=="POST" and request.args['target']=='delete':
        sid=request.args.get("sid")
        response=requests.delete("http://127.0.0.1:5000/api/service/delete",json={"s_id":sid})
        if response.status_code==200:
            flash("service deleted")
            return redirect("/admin/dashboard/")
        else:
            flash("Error in deletion. Try again")
            return redirect("/admin/dashboard/")

    


@app.route('/logout')
@login_required
def user_logout():
    logout_user()
    return redirect('/login')

    

if __name__=="__main__":
    
    app.run(debug=True)