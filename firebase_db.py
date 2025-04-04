import firebase_admin
from firebase_admin import credentials, firestore
import os

class FirebaseDB:
    def __init__(self, config):
        cert_path = config['FIREBASE'].get('CERTIFICATE_PATH', '')
        project_id = config['FIREBASE'].get('PROJECT_ID', '')
        if not firebase_admin._apps:
            if cert_path and os.path.exists(cert_path):
                cred = credentials.Certificate(cert_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id
                })
            else:
                # For testing only – in production provide a valid certificate
                firebase_admin.initialize_app()
        self.db = firestore.client()

    def set_user_interest(self, user_id, interest):
        doc_ref = self.db.collection('users').document(str(user_id))
        doc_ref.set({'interest': interest}, merge=True)

    def get_user_interest(self, user_id):
        doc_ref = self.db.collection('users').document(str(user_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get('interest', None)
        return None

    def get_users_by_interest(self, interest):
        users_ref = self.db.collection('users')
        query = users_ref.where('interest', '==', interest)
        results = query.stream()
        return [doc.id for doc in results]
