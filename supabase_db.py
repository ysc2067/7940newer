# supabase_db.py
from supabase import create_client, Client

class SupabaseDB:
    def __init__(self):
        url = "https://kllkzqxmdmlqmuaohgdg.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtsbGt6cXhtZG1scW11YW9oZ2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NTY0MzIsImV4cCI6MjA1OTQzMjQzMn0.wEp4BFqZgPdhfQJAseCs3PHLa8KDv-mofZZRqG0Uq0A"
        self.client: Client = create_client(url, key)

    def set_user_interest(self, user_id, interest):
        data = {"user_id": str(user_id), "interest": interest}
        self.client.table("users").upsert(data).execute()

    def get_user_interest(self, user_id):
        res = self.client.table("users").select("interest").eq("user_id", str(user_id)).execute()
        if res.data:
            return res.data[0]['interest']
        return None

    def get_users_by_interest(self, interest):
        res = self.client.table("users").select("user_id").eq("interest", interest).execute()
        return [row['user_id'] for row in res.data]

    def clear_user_interest(self, user_id):
        res = self.client.table("users").delete().eq("user_id", str(user_id)).execute()
        return bool(res.data) or res.status_code in [200, 204]

