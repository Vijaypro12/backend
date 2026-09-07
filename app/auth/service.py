from supabase import Client


class AuthService:

    def __init__(self, supabase: Client):
        self.supabase = supabase

    def signup(self, email: str, password: str):
        response = self.supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        return response

    def login(self, email: str, password: str):
        response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        return response

    def request_password_reset(self, email: str, redirect_to: str):
        return self.supabase.auth.reset_password_for_email(
            email,
            options={"redirect_to": redirect_to}
        )

    def update_password(self, access_token: str, password: str, refresh_token: str):
        self.supabase.auth.set_session(access_token, refresh_token)
        return self.supabase.auth.update_user({"password": password})

    def logout(self):
        return self.supabase.auth.sign_out()