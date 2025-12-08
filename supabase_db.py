from supabase import create_client, Client

class SupabaseDB:
    def __init__(self):
        url = "https://kllkzqxmdmlqmuaohgdg.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtsbGt6cXhtZG1scW11YW9oZ2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NTY0MzIsImV4cCI6MjA1OTQzMjQzMn0.wEp4BFqZgPdhfQJAseCs3PHLa8KDv-mofZZRqG0Uq0A"
        self.client: Client = create_client(url, key)

    def set_user_interest(self, user_id, new_interest):
        response = self.client.table("users").select("interest").eq("user_id", user_id).execute()

        if response.data:
            old_interest = response.data[0]['interest']

            self.client.table("users").delete().eq("user_id", user_id).execute()
            self.client.table("users").insert({"user_id": user_id, "interest": new_interest}).execute()

            return f"Your interest '{new_interest}' has replaced your previous interest '{old_interest}'."
        else:
            self.client.table("users").insert({"user_id": user_id, "interest": new_interest}).execute()
            return f"Your interest '{new_interest}' has been saved."

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

