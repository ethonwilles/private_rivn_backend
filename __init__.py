

import pymysql
from sqlalchemy import create_engine, update
import urllib
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, render_template, send_from_directory

from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep




params = pymysql.connect(user="jtippets@rivn-db-dev", password='Jacks0n1', host="rivn-db-dev.mysql.database.azure.com", port=3306, database="delete_vendors")

conn_str = "mysql+pymysql:///{}?charset=utf8mb4".format(params)
engine_azure = create_engine(conn_str,echo=True)

app = Flask(__name__)
cors = CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://jtippets@rivn-db-dev:Jacks0n1@rivn-db-dev.mysql.database.azure.com:3306/delete_vendors"


db = SQLAlchemy(app)

check_place = 0


class VendorCatalog(db.Model):
    __tablename__ = "catalog"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    vendor_id = db.Column(db.String(100))
    image = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    action_url = db.Column(db.String(100))
    action_type = db.Column(db.String(10))
    version = db.Column(db.String(10))
    active = db.Column(db.String(5))
    display = db.Column(db.String(5))

    def __init__(self, name, vendor_id, image, description, action_url, action_type, version, active, display):
        self.name = name
        self.vendor_id = vendor_id
        self.image = image
        self.description = description
        self.action_url = action_url
        self.action_type = action_type
        self.version = version
        self.active = active
        self.display = display




class VendorForm(db.Model):
    __tablename__ = "vendorform"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    vendor_id = db.Column(db.String(100))
    description = db.Column(db.String(500))
    page_variable_type = db.Column(db.String(100))
    page_variable_value = db.Column(db.String(100))
    action_type = db.Column(db.String(10))
    fields = db.Column(db.String(500))
    version = db.Column(db.String(10))
    active = db.Column(db.String(5))
    

    def __init__(self, name, vendor_id, description,page_variable_type, page_variable_value, action_type, fields, version, active):
        self.name = name
        self.vendor_id = vendor_id
        self.description = description
        self.page_variable_type = page_variable_type
        self.page_variable_value = page_variable_value
        self.action_type = action_type
        self.fields = fields
        self.version = version
        self.active = active
        
class Cookies(db.Model):
    __tablename__ = "cookie_catalog"
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.String(100))
    cookie_id = db.Column(db.String(100))
    
    def __init__(self, vendor_id, cookie_id):
        self.vendor_id = vendor_id
        self.cookie_id = cookie_id

class URLS(db.Model):
    __tablename__ = "audit_catalog"
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.String(100))
    vendor_url = db.Column(db.String(100))

    def __init__(self, vendor_id, vendor_url):
        self.vendor_id = vendor_id
        self.vendor_url = vendor_url
class AuditResults(db.Model):
    __tablename__ = "cleandup"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))
    full_list = db.Column(db.String(500))
    has_consent = db.Column(db.Boolean)
    consent_html = db.Column(db.Text)
    has_privacy = db.Column(db.Boolean)
    privacy_url = db.Column(db.Text)





class RivnScrape():
    def __init__(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://jtippets@rivn-db-dev:Jacks0n1@rivn-db-dev.mysql.database.azure.com:3306/audit_results"
class BackToNormal():
    def __init__(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://jtippets@rivn-db-dev:Jacks0n1@rivn-db-dev.mysql.database.azure.com:3306/delete_vendors"
class CheckPlace():
    def __init__(self, num):
        self.num = num


### CATALOG SECTION ###
@app.route("/atlassian-domain-verification.html", methods=["GET"])
def render_atlas():
	return render_template("jira.html")
@app.route("/", methods=["GET"])
def render_react_app():
	return render_template("index.html")

@app.route("/new-vendor-catalog", methods=["POST"])
def post_new_member():
    vendor_id = request.json["vendor_id"]
    if VendorCatalog.query.filter_by(vendor_id=vendor_id).first():
        return {"CREATED" : False, "ALREADY_EXISTS" : True}
    else:

        try:
            name = request.json["name"]
            vendor_id = request.json["vendor_id"]
            image = request.json["image"]
            description = request.json["description"]
            action_type= request.json["action_type"]
            action_url = request.json["action_url"]
            version = request.json["version"]
            active = request.json["active"]
            display = request.json["display"]

            new_member = VendorCatalog(name, vendor_id, image, description, action_type, action_url, version, active, display)
            db.session.add(new_member)
            db.session.commit()
            
            
            return {"CREATED": True}, 200
        except Exception as e:
            return {"CREATED" : False, "CODE" : "{}".format(e)}


@app.route("/list-all-vendors", methods=["GET"])
def get_names():
    all_users = VendorCatalog.query.all()
    Request = {}
    all_vendors = []
    
    for user in all_users:
        
        Request["name"] = user.name
        Request['vendor_id'] = user.vendor_id
        Request["image"] = user.image
        Request['description'] = user.description
        Request['action_type'] = user.action_type
        Request['action_url'] = user.action_url
        Request['version'] = user.version
        Request['active'] = user.active
        Request['display'] = user.display

        all_vendors.append(Request)
        Request = {}

        
    
    return {"vendors" : all_vendors}

@app.route("/edit-vendor-catalog", methods=["POST"])
def edit_vendor():
    
        
            try:
                name = request.json["name"]
                vendor_id = request.json["vendor_id"]
                image = request.json["image"]
                description = request.json["description"]
                action_type= request.json["action_type"]
                action_url = request.json["action_url"]
                version = request.json["version"]
                active = request.json["active"]
                display = request.json["display"]

                user_found = VendorCatalog.query.filter_by(name=name).first()
                
                
                user_found.name = name
                user_found.vendor_id = vendor_id
                user_found.image = image
                user_found.description = description
                user_found.action_type = action_type
                user_found.action_url = action_url
                user_found.version = version
                user_found.active = active
                user_found.display = display
                
                db.session.commit()
                user_found = VendorCatalog.query.filter_by(name=name).first()
                vendor = {}
                
                vendor["name"] = user_found.name
                vendor['vendor_id'] = user_found.vendor_id
                vendor['description'] = user_found.description
                vendor["image"] = user_found.image
                vendor['action_type'] = user_found.action_type
                vendor['action_url'] = user_found.action_url
                vendor['version'] = user_found.version
                vendor['active'] = user_found.active
                vendor['display'] = user_found.display

                
                return {"CREATED" : True}, 200
            except Exception as e:
                return {"USER_FOUND" : False, "ERROR" : "{}".format(e)}, 500
    
        
@app.route("/get-vendor-catalog", methods=["POST"])
def get_vendor_catalog():
    method_of_change = request.json["method"]
    if method_of_change == "name":
        try:
                name = request.json['name']
                user_found = VendorCatalog.query.filter_by(name=name).first()
                vendor = {}
                        
                vendor["name"] = user_found.name
                vendor['vendor_id'] = user_found.vendor_id
                vendor['description'] = user_found.description
                vendor["image"] = user_found.image
                vendor['action_type'] = user_found.action_type
                vendor['action_url'] = user_found.action_url
                vendor['version'] = user_found.version
                vendor['active'] = user_found.active
                vendor['display'] = user_found.display
                
                return vendor, 200
        except Exception as e:
            return {'USER_FOUND' : False, "ERROR" : "{}".format(e)}, 500
    elif method_of_change == 'vendor_id':
        try:
                vendor_id = request.json["vendor_id"]
                user_found = VendorCatalog.query.filter_by(vendor_id=vendor_id).first()
                vendor = {}
                        
                vendor["name"] = user_found.name
                vendor['vendor_id'] = user_found.vendor_id
                vendor['description'] = user_found.description
                vendor["image"] = user_found.image
                vendor['action_type'] = user_found.action_type
                vendor['action_url'] = user_found.action_url
                vendor['version'] = user_found.version
                vendor['active'] = user_found.active
                vendor['display'] = user_found.display
                
                return vendor, 200
        except Exception as e:
            return {'USER_FOUND' : False, "ERROR" : "{}".format(e)}, 500


### VENDORFORM SECTION ###

@app.route("/new-vendor-form", methods=["POST"])
def post_new_member_form():
    vendor_id = request.json["vendor_id"]
    if VendorForm.query.filter_by(vendor_id=vendor_id).first():
        return {"CREATED" : False, "ALREADY_EXISTS" : True}
    else:

        try:
            name = request.json["name"]
            vendor_id = request.json["vendor_id"]
            description = request.json["description"]
            page_variable_value = request.json["page_variable_value"]
            page_variable_type = request.json["page_variable_type"]
            action_type= request.json["action_type"]
            fields = request.json["fields"]
            version = request.json["version"]
            active = request.json["active"]
            

            new_member = VendorForm(name, vendor_id, description,page_variable_type, page_variable_value, action_type, fields, version, active)
            db.session.add(new_member)
            db.session.commit()
            
            
            return {"CREATED": True}, 200
        except Exception as e:
            return {"CREATED" : False, "CODE" : "{}".format(e)}


@app.route("/edit-vendor-form", methods=["GET","POST"])
def edit_vendor_form():
    
            try:
                name = request.json["name"]
                vendor_id = request.json["vendor_id"]
                description = request.json["description"]
                page_variable_value = request.json["page_variable_value"]
                page_variable_type = request.json["page_variable_type"]
                action_type= request.json["action_type"]
                fields = request.json["fields"]
                version = request.json["version"]
                active = request.json["active"]

                user_found = VendorForm.query.filter_by(vendor_id=vendor_id).first()
                
                
                user_found.name = name
                user_found.vendor_id = vendor_id
                user_found.description = description
                user_found.page_variable_type = page_variable_type
                user_found.page_variable_value = page_variable_value
                user_found.action_type = action_type
                user_found.fields = fields
                user_found.version = version
                user_found.active = active
                
                
                db.session.commit()
                
                

                
                return {"CREATED" : True}, 200
            except Exception as e:
                return {"USER_FOUND" : False, "ERROR" : "{}".format(e)}

@app.route("/get-vendor-form", methods=["POST"])
def get_vendor_form():
    method_of_change = request.json["method"]
    if method_of_change == "name":
        try:
                name = request.json['name']
                user_found = VendorForm.query.filter_by(name=name).first()
                vendor = {}
                        
                vendor["name"] = user_found.name
                vendor['vendor_id'] = user_found.vendor_id
                vendor['description'] = user_found.description
                vendor["page_variable_type"] = user_found.page_variable_type
                vendor["page_variable_value"] = user_found.page_variable_value
                vendor['action_type'] = user_found.action_type
                vendor["fields"] = user_found.fields
                vendor['version'] = user_found.version
                vendor['active'] = user_found.active
                
                return vendor, 200
        except Exception as e:
            return {'USER_FOUND' : False, "ERROR" : "{}".format(e)}
    elif method_of_change == 'vendor_id':
        try:
                vendor_id = request.json["vendor_id"]
                user_found = VendorForm.query.filter_by(vendor_id=vendor_id).first()
                vendor = {}
                        
                vendor["name"] = user_found.name
                vendor['vendor_id'] = user_found.vendor_id
                vendor['description'] = user_found.description
                vendor["page_variable_type"] = user_found.page_variable_type
                vendor["page_variable_value"] = user_found.page_variable_value
                vendor['action_type'] = user_found.action_type
                vendor["fields"] = user_found.fields
                vendor['version'] = user_found.version
                vendor['active'] = user_found.active
                
                return vendor, 200
        except Exception as e:
            print(Exception)
            return {'USER_FOUND' : False, "ERROR" : "{}".format(e)}

@app.route("/list-all-forms", methods=["GET"])
def get_names_form():
    all_users = VendorForm.query.all()
    Request = {}
    all_vendors = []
    
    for user in all_users:
        
        Request["name"] = user.name
        Request['vendor_id'] = user.vendor_id
        Request['description'] = user.description
        Request["page_variable_type"] = user.page_variable_type
        Request["page_variable_value"] = user.page_variable_value
        Request['action_type'] = user.action_type
        Request["fields"] = user.fields
        Request['version'] = user.version
        Request['active'] = user.active

        all_vendors.append(Request)
        Request = {}

        
    
    return {"vendors" : all_vendors}
# Cookies and URLS

@app.route("/cookies", methods=["POST"])
def get_cookie():
    if request.json["change"]:
       
            cookie_list = request.json["cookie_list"]

            vendor_id = request.json["vendor_id"]
            cookie = Cookies.query.filter_by(vendor_id=vendor_id).first()
            cookie.cookie_id = cookie_list
            
            db.session.commit()
            return {"SUCCESS" : True}
        
    else: 
        
        try:
            vendor_id = request.json["vendor_id"]
            cookie = Cookies.query.filter_by(vendor_id=vendor_id).first()
            
            
            db.session.commit()
            return {"cookies" : list(cookie.cookie_id.split(" "))}
        except:
            return {"SUCCESS" : False}


@app.route("/urls", methods=["POST"])
def get_urls():
    if request.json["change"]:
        cookie_list = request.json["cookie_list"]
        vendor_id = request.json["vendor_id"]
        url = URLS.query.filter_by(vendor_id=vendor_id).first()
        url.vendor_url = cookie_list
        db.session.commit()

        return {"SUCCESS" : True}

    else:
        try:
            vendor_id = request.json["vendor_id"]
            url = URLS.query.filter_by(vendor_id=vendor_id).first()
        
            return {"cookies" : list(url.vendor_url.split(" "))} 
        except Exception as e:
            print(e)
            return {"SUCCESS" : False}
@app.route('/audit-results-urls', methods=["GET"])
def test():
    global check_place
    RivnScrape()
    results = []
    length_of_audit = AuditResults.query.all()
    for i in length_of_audit:
        if i.id >= check_place:
            results.append(i.url)
    
    
    BackToNormal()
    
    return {"results" : results} 
   
@app.route("/audit-results-post", methods=["POST"])
def post():
        RivnScrape()
        url = request.json["url"]
        if request.json["choice"] == "privacy":
    
            bool_priv = request.json["has_priv"]
            
            priv_url = request.json["priv_url"]
            
            url = request.json["url"]

            item = AuditResults.query.filter_by(url=url).first()
            item.has_privacy = bool_priv
            item.privacy_url = priv_url
            
            

            print(bool_priv, " ", priv_url)

            
            db.session.commit()
        elif request.json["choice"] == "cookie":
            
            bool_cook = request.json["has_cook"]
            cons_html = request.json["html"]
            url = request.json["url"]

            item = AuditResults.query.filter_by(url=url).first()
            item.has_consent = bool_cook
            item.consent_html = cons_html
            db.session.commit()
        elif request.json["choice"] == "cookie boolean":
            bool_cook = request.json["has_cook"]
            url = request.json["url"]

            item = AuditResults.query.filter_by(url=url).first()
            item.has_consent = bool_cook
            db.session.commit()
        elif request.json["choice"] == "privacy boolean":
            bool_priv = request.json["has_priv"]
            url = request.json["url"]

            item = AuditResults.query.filter_by(url=url).first()
            item.has_privacy = bool_priv
            db.session.commit()
        
        item = AuditResults.query.filter_by(url=url).first()
        vendor = {}
        vendor["id"] = item.id
        vendor["url"] = item.url
        
        vendor["has_consent"] = item.has_consent
        vendor["consent_html"] = item.consent_html
        vendor["has_privacy"] = item.has_privacy
        vendor["privacy_url"] = item.privacy_url

        BackToNormal()

        return vendor
@app.route("/new-placeholder", methods=["GET","POST"])
def new_placeholder():
    global check_place
    if request.method == "POST":
        
        old_placeholder = check_place
        new_placeholder = request.json["number"]
        check_place = new_placeholder
        return {"OLD" : old_placeholder, "new" : check_place}
    elif request.method == "GET":
        
        return {"num" :check_place}
@app.route("/get-info/<url>", methods=["GET"])
def get_info(url):
	RivnScrape()
	item = AuditResults.query.filter_by(url=url).first()
	query = { "html" : item.consent_html, "cons" : item.has_consent, "priv_url" : item.privacy_url, "has_priv" : item.has_privacy, "url" : item.url, "id" : item.id}
	BackToNormal()
	return query









######## IMAGE SERVER ##########
@app.route("/take-screenshot", methods=["POST"])
def take_screenshot():
    
    url = request.json["url"]
    
    
        
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get('https://{}.com'.format(url))
    sleep(1)
    driver.save_screenshot('{}.png'.format(url))
    driver.quit()
    return send_from_directory("static", filename="{}.png".format(url))
    #     else:
        
    #         options = Options()
    #         options.add_argument("--headless")
    #         options.add_argument("--disable-gpu")
    #         options.add_argument("--disable-dev-shm-usage")
    #         options.add_argument("--no-sandbox")
    #         driver = webdriver.Chrome(options=options)
    #         url = "https://www.{}.com".format(url)
    #         driver.get(url)
    #         sleep(1)                                                                                                      
    #         driver.find_element_by_tag_name('body').screenshot('./static/{}.png'.format(url))
    #         driver.quit()
    #     return send_from_directory("static", filename="{}.png".format(url))
    # except Exception as e:
    #     return "{}".format(e)
if __name__ == "__main__":
    app.run(debug=True)
