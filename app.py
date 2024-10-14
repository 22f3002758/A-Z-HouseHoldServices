from flask import Flask,request, render_template, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey,Nullable
from flask_login import LoginManager, login_user, logout_user, login_required, current_user,UserMixin
import datetime
import matplotlib.pyplot as plt

app=Flask(__name__)# create constructor
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
app.config['SECRET_KEY']="mysecretkey"
db = SQLAlchemy(app) # connect app with sqlalchemy

login_manager=LoginManager(app)

app.app_context().push()# push it in the server



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
    sp_warn=db.Column(db.Integer)
    sp_warn_msg=db.Column(db.String)
    sp_servicename=db.Column(db.String,db.ForeignKey("services.s_name"))
    mypackages=db.relationship("Package", backref="servprovider")
    receive_request=db.relationship("Request",backref="servprovider")
    

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
    c_warn=db.Column(db.Integer)
    c_warn_msg=db.Column(db.String)
    Sent_Request=db.relationship("Request",backref="cust")
    
    def get_id(self):
       return f'c-{self.c_id}'  

class Services(db.Model):
    __tablename__="services"

    s_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    s_name=db.Column(db.String,unique=True)
    baseprice=db.Column(db.Integer)
    packages=db.relationship("Package", backref="service")
    Sproviders=db.relationship("ServiceProvider",backref="service")
    

      
class Package(db.Model):
    __tablename__="package"

    p_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    p_name=db.Column(db.String,unique=True)
    p_price=db.Column(db.Integer)
    p_description=db.Column(db.String)
    p_rating=db.Column(db.Integer)
    s_id=db.Column(db.Integer, db.ForeignKey("services.s_id"),nullable=False)
    sp_id=db.Column(db.Integer, db.ForeignKey("serviceprovider.sp_id"),nullable=False)
    req=db.relationship("Request",backref="pack")


class Request(db.Model):
    __tablename__="request"

    r_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    # s_id=db.Column(db.Integer, ForeignKey(services.s_id),nullable=False)
    sp_id=db.Column(db.Integer, db.ForeignKey("serviceprovider.sp_id"),nullable=False)
    c_id=db.Column(db.Integer, db.ForeignKey("customer.c_id"),nullable=False)
    p_id=db.Column(db.Integer, db.ForeignKey("package.p_id"),nullable=False)
    r_date=db.Column(db.String)
    r_time=db.Column(db.String)
    r_address=db.Column(db.String)
    r_city=db.Column(db.String)
    r_message=db.Column(db.String)
    r_status=db.Column(db.String)
    r_rating=db.Column(db.Integer)
    all_messages=db.relationship("Messages",backref="req")

class Messages(db.Model):
    __tablename__="messages"  

    m_id=db.Column(db.Integer, primary_key=True, autoincrement= True)
    r_id=db.Column(db.Integer, db.ForeignKey("request.r_id"),nullable=False)
    m_content=db.Column(db.String)
    m_sender=db.Column(db.String)

# class Warning(db.Model):
#     __tablename__="warning"

#     w_id=db.Column(db.Integer, primary_key=True, autoincrement= True)  
#     w_content=db.Column(db.String)
#     w_reciever=db.Column(db.String) 
    



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
            cust=Customer(c_name=cname,c_address=caddress, c_pincode=cpincode,c_email=cemail,c_pwd=cpwd,c_phone=cphone,c_warn=0)
            db.session.add(cust)
            db.session.commit()   
            return redirect("login.html")
        

    elif request.method=="GET" and request.args["utype"]=="serviceprovider":
        return render_template("/ServiceProvider/register_service.html") 
    elif request.method=="POST" and request.args["utype"]=="serviceprovider":
        spname=request.form.get("s_name")
        spaddress=request.form.get("s_address")
        sppincode=request.form.get("s_pincode")
        spemail=request.form.get("s_email")
        sppwd=request.form.get("s_pwd")  
        spexp=request.form.get("s_exp") 
        spphone=request.form.get("s_phone")
        sp=db.session.query(ServiceProvider).filter_by(sp_email=spemail).first()
        if sp:
            return redirect("/exist")
        else:
            sp=ServiceProvider(sp_name=spname,sp_address=spaddress, sp_pincode=sppincode,sp_email=spemail,
                               sp_pwd=sppwd,sp_phone=spphone,sp_exp=spexp,sp_warn=0,sp_rating=0)
            db.session.add(sp)
            db.session.commit()  
            return redirect("login.html")
        
@app.route("/profile-update", methods=["GET","POST"])
def update():
    if request.method=="POST" and request.args.get("utype")=="customer":
        cu=current_user
        cn=request.form.get("cname")
        ce=request.form.get("cemail")
        cc=request.form.get("ccity")
        cp=request.form.get("phone")
        ca=request.form.get("cadd")
        cpwd=request.form.get("cpwd")
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
        return redirect("/customer/Dashboard")    


@login_manager.user_loader
def load_user(user_id):
        utype,id=user_id.split("-")
        if utype=="c":
            return db.session.query(Customer).filter_by(c_id=id).first()
        elif utype=='sp':
            return db.session.query(ServiceProvider).filter_by(sp_id=id).first()
        else:
            return db.session.query(Admin).filter_by(admin_id=id).first()


  


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
def book():
    if request.method=="POST" and "edit" in request.args:
        rid=request.args.get("rid")
        edate=request.form.get("Date")
        etime=request.form.get("Time")
        emsg=request.form.get("msg")
        edit_req=db.session.query(Request).filter_by(r_id=rid).first()
        edit_req.r_date=edate
        edit_req.r_time=etime
        edit_req.r_message=emsg
        db.session.commit()
        return redirect("/customer/Dashboard")
    elif request.method=="POST" and "delete" in request.args:
        rid=request.args.get("rid")
        print("start")
        delete_req=db.session.query(Request).filter_by(r_id=rid).first()
        db.session.delete(delete_req)
        db.session.commit()
        print("Done")
        return redirect("/customer/Dashboard")
    elif request.method=="POST" and "close" in request.args:
        rid=request.args.get("rid")
        
        close_req=db.session.query(Request).filter_by(r_id=rid).first()
        close_req.r_status="Closed"
        db.session.commit()
        
        return redirect("/customer/Dashboard")
    elif request.method == "POST":
        spid=request.args.get("spid")
        pid=request.args.get("pid")
        print(pid)
        cid=current_user.c_id
        rdate = request.form.get("Date")
        rtime = request.form.get("Time")
        print(rdate,rtime)
        raddress = request.form.get("c_add")
        rcity = request.form.get("c_city")
        rmsg = request.form.get("msg")
        rstatus = "Requested"
        R= Request(sp_id=spid,p_id=pid,c_id=cid,r_date=rdate, r_time=rtime,r_address=raddress,r_city=rcity,r_message=rmsg,r_status=rstatus,r_rating=0)
        db.session.add(R)
        db.session.commit()
        return redirect("/customer/Dashboard")
    
@app.route("/rating",methods=["GET","POST"])
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
def search():
        
    if request.method=="GET" and "sname" in request.args:
        
        s=request.args.get("sname")
        ser=db.session.query(Services).filter_by(s_name=s).first()
        pack=ser.packages
        Servis=db.session.query(Services).all()
        return render_template("/Customer/custsearch.html",package=pack,Services=Servis,cu=current_user)
    
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
        return render_template("/Customer/custsearch.html",package=pack,Services=Servis,cu=current_user)
        

@app.route("/customer/stats",methods=["GET","POST"])  
def cus_stats():
    if request.method=="GET":
        cu=current_user 
        
        f=[0,0,0]
        c_req=current_user.Sent_Request
        for req in c_req:
            d=req.r_date.split("-")
            if req.r_status=="Accepted":
                f[0]+=1
            elif req.r_status=="Rejected":
                f[1]+=1
            elif req.r_status=="Closed":
                f[2]+=1       
        X=["Accepted","Rejected","Closed"]
        plt.bar(X, f, color='r')
        
        plt.savefig("./static/cus/bar1.png")

        return render_template("/customer/cus_stats.html",cu=cu)
    

@app.route("/admin/stats",methods=["GET","POST"])  
def ad_stats():
    if request.method=="GET":
        cu=current_user 
        req=db.session.query(Request).all()
        
        f=[0,0,0]
        
        for r in req:
            
            if r.r_status=="Accepted":
                f[0]+=1
            elif r.r_status=="Requested":
                f[1]+=1
            elif r.r_status=="Closed":
                f[2]+=1       
        X=["Accepted","Rejected","Closed"]
        plt.bar(X, f, color='r')
        
        plt.savefig("./static/ad/bar1.png")

        return render_template("/admin/ad_stats.html",cu=cu)   
        

@app.route("/serviceprovider/dashboard", methods=["GET","POST"])
@login_required
def SPDashboard():
    
    if request.method=="GET" and "accept" in request.args:
        
        id=request.args.get("rid")
        r=db.session.query(Request).filter_by(r_id=id).first()
        r.r_status="Accepted"
        db.session.commit()
        return redirect("/serviceprovider/dashboard")
    elif request.method=="POST" and "reject" in request.args:
        id=request.args.get("rid")
        r=db.session.query(Request).filter_by(r_id=id).first()
        r.r_status="Rejected"
        db.session.commit()
        return redirect("/serviceprovider/dashboard")
    elif request.method=="GET":
        d=datetime.date.today()
        cd = d.strftime("%d-%m-%Y")
        r=db.session.query(Request).filter_by(sp_id=current_user.sp_id,r_date=cd,r_status="Accepted").all()
        Opser=db.session.query(Request).filter_by(sp_id=current_user.sp_id,r_status="Accepted").all()
        reqser=db.session.query(Request).filter_by(sp_id=current_user.sp_id,r_status="Requested").all()
        closeser=db.session.query(Request).filter_by(sp_id=current_user.sp_id,r_status="Closed").all()
        mypack=current_user.mypackages
        rate=0
        for p in mypack:
            rate+=p.p_rating
        rating=rate/len(mypack)
        
        current_user.sp_rating=rating
        db.session.commit()
        print(current_user.sp_rating)
        return render_template("/ServiceProvider/serviceprovider.html",cu=current_user,
                               rating=current_user.sp_rating,todays_requests=r,open_services=Opser,requested_services=reqser,closed_services=closeser)

@app.route("/serviceprovider/create",methods=["GET","POST"])
def create_pack():
    if request.method=="GET":
        P=db.session.query(Package).filter_by(sp_id=current_user.sp_id).all()
        return render_template("/ServiceProvider/create_package.html",mypackage=P)
    elif request.method=="POST" and "edit" in request.args:
        pid=request.args.get("pid")
        pn=request.form.get("pname")
        pd=request.form.get("pdesc")
        pp=request.form.get("pprice")
        edit_pack=db.session.query(Package).filter_by(p_id=pid).first()
        if pn:
            edit_pack.p_name=pn
        if pd:
            edit_pack.p_description=pd
        if pp:
            edit_pack.p_price=pp
        db.session.commit()
        return redirect("/serviceprovider/create")
    elif request.method=="POST" and "create" in request.args:
        
        pn=request.form.get("pname")
        pd=request.form.get("pdesc")
        pp=request.form.get("pprice")
        create_pack=Package(p_price=pp,p_name=pn,p_description=pd,sp_id=current_user.sp_id,s_id=current_user.service.s_id,p_rating=0)
        db.session.add(create_pack)
        db.session.commit()
        return redirect("/serviceprovider/create")
    
@app.route("/serviceprovider/stats",methods=["GET","POST"])  
def stats():
    if request.method=="GET":
        cu=current_user 
        f=[0,0,0]
        sp_req=current_user.receive_request
        for req in sp_req:
            d=req.r_date.split("-")
            if req.r_status=="Accepted":
                f[0]+=1
            elif req.r_status=="Rejected":
                f[1]+=1
            elif req.r_status=="Closed":
                f[2]+=1       
        X=["Accepted","Rejected","Closed"]
        # plot bars in stack manner
        plt.bar(X, f, color='r')
        
        plt.savefig("./static/sp/bar1.png")

        return render_template("/ServiceProvider/sp_stats.html",cu=cu)
             
@app.route("/admin/dashboard/",methods=["GET","POST"]) 
@login_required
def dashboard():
    if request.method=="GET":
        ser=db.session.query(Services).all()
        act_sp=db.session.query(ServiceProvider).filter_by(sp_status="Active").all()
        req_sp=db.session.query(ServiceProvider).filter_by(sp_status="Requested").all()
        flag_sp=db.session.query(ServiceProvider).filter_by(sp_status="Flagged").all()
        act_c=db.session.query(Customer).filter_by(c_status="Active").all()
        flag_c=db.session.query(Customer).filter_by(c_status="Flagged").all()
        print(ser)
        return render_template("/admin/Admin_dashboard.html",Services=ser,active=act_sp,requested=req_sp,flagged=flag_sp,cu=current_user,
                               c_active=act_c,c_flag=flag_c)

@app.route("/flag",methods=["GET","POST"])
def flag():
    if request.method=="POST" and request.args["target"]=="sp" and request.args["action"]=="flag":
        spid=request.args.get("spid")
        sp=db.session.query(ServiceProvider).filter_by(sp_id=spid).first()
        sp.sp_status="Flagged"
        db.session.commit()
        return redirect("/admin/dashboard")
    elif request.method=="POST" and request.args["target"]=="sp" and request.args["action"]=="unflag":
        spid=request.args.get("spid")
        sp=db.session.query(ServiceProvider).filter_by(sp_id=spid).first()
        sp.sp_status="Active"
        db.session.commit()
        return redirect("/admin/dashboard")

    
    elif request.method=="POST" and request.args["target"]=="c" and request.args["action"]=="flag":
        cid=request.args.get("cid")
        c=db.session.query(Customer).filter_by(c_id=cid).first()
        c.c_status="Flagged"
        db.session.commit()
        return redirect("/admin/dashboard")
    elif request.method=="POST" and request.args["target"]=="c" and request.args["action"]=="unflag" :
        cid=request.args.get("cid")
        c=db.session.query(Customer).filter_by(c_id=cid).first()
        c.c_status="Active"
        db.session.commit()
        return redirect("/admin/dashboard")

@app.route("/warning", methods=["GET","POST"])
def warning():
    if request.method=="POST" and request.args["target"]=="sp" and request.args["action"]=="Active":
        spid=request.args.get("spid")
        msg=request.form.get("msg")
        sp=db.session.query(ServiceProvider).filter_by(sp_id=spid).first()
        sp.sp_warn+=1
        sp.sp_warn_msg=msg
        db.session.commit()
        return redirect("/admin/dashboard") 
    elif request.method=="POST" and request.args["target"]=="c" and request.args["action"]=="Active":
        cid=request.args.get("cid")
        msg=request.form.get("msg")
        c=db.session.query(Customer).filter_by(c_id=cid).first()
        c.c_warn+=1
        c.sp_warn_msg=msg
        db.session.commit()
        return redirect("/admin/dashboard")  
    
          
# @app.route("/messages",methods=["GET","POST"])
# def messages():  
#     if request.method=='POST' and          



    
@app.route("/service" , methods=["GET","POST"])
@login_required
def service():
    print("hello")
    if request.method=="POST" and "ns" in request.args:
        sn=request.form.get("servicename")
        # sd=request.form.get("desc")
        bp=request.form.get("baseprice")
        add_ser=Services(s_name=sn,baseprice=bp)
        db.session.add(add_ser)
        db.session.commit()
        return redirect("/admin/dashboard/")
    elif request.method=="POST" and "edit" in request.args:
        sid=request.args.get("sid")
        up_ser=db.session.query(Services).filter_by(s_id=sid).first()
        sn=request.form.get("servicename")
        # sd=request.form.get("desc")
        bp=request.form.get("baseprice")
        if sn:
            up_ser.s_name=sn
        # if sd:
        #     up_ser.s_desc=sd
        if bp:
            up_ser.baseprice=bp
        db.session.commit()
        return redirect("/admin/dashboard/")


@app.route('/logout')
@login_required
def user_logout():
    logout_user()
    return redirect('/login')

if __name__=="__main__":
    app.run(debug=True)