import firebase_admin
from firebase_admin import credentials, firestore
import os

class FirebaseDB:
    def __init__(self, config):
        cert_path = config['FIREBASE'].get('CERTIFICATE_PATH', '')
        project_id = config['FIREBASE'].get('PROJECT_ID', '')

        # 将相对路径转换为绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(cert_path):
            cert_path = os.path.join(script_dir, cert_path)
            print("Debug: Converted cert_path =", cert_path, flush=True)

        # 输出调试信息
        print("Debug: Entering FirebaseDB.__init__", flush=True)
        print("Debug: project_id =", project_id, flush=True)
        print("Debug: cert_path =", cert_path, flush=True)

        # 如果未初始化，则使用证书初始化 Firebase
        if not firebase_admin._apps:
            if cert_path and os.path.exists(cert_path):
                cred = credentials.Certificate(cert_path)
                firebase_admin.initialize_app(cred, {'projectId': project_id})
            else:
                raise FileNotFoundError(f"Service account file not found at {cert_path}")
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
