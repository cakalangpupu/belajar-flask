import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

firebaseConfig = {
    "apiKey": "AIzaSyCUDxRi3atGFkPxDzuno154kBu8WKCAa5U",
    "authDomain": "siakad-6c22c.firebaseapp.com",
    "databaseURL": "https://siakad-6c22c-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "siakad-6c22c",
    "storageBucket": "siakad-6c22c.appspot.com",
    "messagingSenderId": "769825188323",
    "appId": "1:769825188323:web:816844c32d4384acc6d8d6"
}
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()


def get_all_collection(collection, orderBy=None, direction=None):
    if orderBy:
        collects_ref = db.collection(collection).order_by(
            orderBy, direction=direction)
    else:
        collects_ref = db.collection(collection)
    collects = collects_ref.stream()
    RETURN = []
    for collect in collects:
        ret = collect.to_dict()
        ret['id'] = collect.id
        RETURN.append(ret)
    return RETURN