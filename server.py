from flask import Flask, jsonify, request
from flask_cors import CORS
import pyrebase
import hashlib
import os
import img_gen
import imgToPDF
import Encryption
from firebase_admin import credentials, firestore, initialize_app
import face_Enc
from flask_mail import Mail,Message


app = Flask(__name__)
CORS(app)


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "serviceAccountkey.json"
config = {
  "apiKey": "AIzaSyBQ6MkAyHwLgvRbf-Xex8bREQnHs8ueIPE",
  "authDomain": "docs-e7c78.firebaseapp.com",
  "databaseURL":"gs://docs-e7c78.appspot.com",
  "projectId": "docs-e7c78",
  "storageBucket": "docs-e7c78.appspot.com",
  "serviceAccount": "serviceAccountkey.json"
};

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = '465'
app.config['MAIL_USERNAME'] = 'nchandra458.n@gmail.com'
app.config['MAIL_PASSWORD'] = 'qlvvdlvauburcfow'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
#firestore
cred = credentials.Certificate("serviceAccountkey.json")
default_app = initialize_app(cred)
db = firestore.client()
docs = db.collection('docs')

#firebase
firebase_storage = pyrebase.initialize_app(config)
st = firebase_storage.storage()


UPLOAD_FOLDER = "C:/Users/nchan/Desktop/Capstone/Database"




@app.route('/upload', methods = ['POST'])
def Upload():
    upload = request.files["newfile"]
    upload.save(upload.filename)

    if upload.filename[-4:] == ".pdf":
    # print(app.root_path)
        
        
        secret_key = request.form['key']
        emailid = request.form['id']
        doc_name = img_gen.convert(upload.filename)

        
        
        result = hashlib.sha256(secret_key.encode())
        
        key=os.urandom(32)
        doc_name = Encryption.encyption(doc_name,key,result.hexdigest())
        doc_name = result.hexdigest() + ".png"
        print(doc_name)
        data = Encryption.getData(doc_name)
        msg = Message("encrypted aadhar document",sender= 'noreply@gmail.com',recipients=[emailid])
        msg.body = "Thank you for using our application.\n This is your encrypted aadhar copy"
        with app.open_resource(doc_name) as fp:
            msg.attach(doc_name,"image/png", fp.read())
        mail.send(msg)

        imgToPDF.convert(doc_name)
        st.child(f"{doc_name[:-4]}/document.pdf").put(doc_name[:-4]+".pdf") #encrypted document
        
        url = st.child(f"{doc_name[:-4]}/document.pdf").get_url("document.pdf")
        result = hashlib.sha256(data.encode())
        docs.document(doc_name[:-4]).set({"encryption": result.hexdigest()}, merge=True)
        print(result.hexdigest())



        msg = Message("encrypted aadhar document",sender= 'noreply@gmail.com',recipients=[emailid])
        msg.body = "Thank you for using our application.\n This is your encrypted aadhar copy"
        with app.open_resource(doc_name[:-4]+".pdf") as fp:
            msg.attach(doc_name[:-4]+".pdf","application/pdf", fp.read())
        mail.send(msg)

        addDocFirestore(doc_name,url)


    else:

    #     image = request.files['image']
    # image.save(image.filename)
        secret_key = request.form['key']
        secret_key = hashlib.sha256(secret_key.encode())
        doc_name = secret_key.hexdigest()
        st.child(f"{doc_name}/personal_image.jpg").put(upload.filename)
        url = st.child(f"{doc_name}/personal_image.jpg").get_url("personal_image.jpg")
        addImgFirestore(doc_name,url)
            
    return "Sucessful"




# API Route
@app.route('/verify', methods = ['POST'])
def Verify():
    fil = request.files['file']
    img = request.files['newfile']
    
    img.save(img.filename)
    fil.save(fil.filename)
    # file encryption
    
    if fil.filename[-4:] != ".png":
        temp = fil
        fil = img
        img = temp
    
    doc = fil.filename
    
    print(img.filename)
    print(fil.filename)

    secret_key = request.form['key']
    secret_key = hashlib.sha256(secret_key.encode())
    doc_name = secret_key.hexdigest()
    enc = Encryption.getData(doc)
    enc = hashlib.sha256(enc.encode())
    enc = enc.hexdigest()
    print(enc)
    doc_enc = docs.document(doc_name).get().to_dict()['encryption']

    #image comparison

    # print(img.filename)
    # print(fil.filename)
    # print(enc)
    # print(doc_enc)
    if face_Enc.face_enc(img.filename,docs.document(doc_name).get().to_dict()['img_url']) and enc == doc_enc:
        return "Verified"

    else:
        return "Not Verified"
    


def addDocFirestore(name,url):

    docs.document(name[:-4]).set({"doc_url": url}, merge=True)
    return jsonify({"success": True}), 200
    

def addImgFirestore(name,url):

    
    docs.document(name).set({"img_url": url}, merge=True )
    return jsonify({"success": True}), 200
    


if __name__ == "__main__":
    app.run(debug = True)
