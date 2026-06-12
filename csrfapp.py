import secrets

# ---------------- CSRF VULNERABLE ----------------
@app.route("/secure-change-password", methods=["GET", "POST"])
def secure_change_password():
    if "user" not in session:
        return redirect("/login")

    if request.method == "GET":
        token = secrets.token_hex(16)
        session["csrf_token"] = token
        return f"""
        <form method="POST">
            <input type="hidden" name="csrf_token" value="{token}">
            <input type="password" name="password">
            <button type="submit">Change</button>
        </form>
        """

    if request.form.get("csrf_token") != session.get("csrf_token"):
        return "CSRF Attack Detected!"

    return "Password Changed Securely"
