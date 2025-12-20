from flet import *
import requests
import mkmsg
import os
from dotenv import load_dotenv
import time
import threading
import random

load_dotenv()




global otp_code
otp_code = mkmsg.generate_otp(6)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>OTP Code</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f6f8;">

<table width="100%" height="100%" cellpadding="0" cellspacing="0" role="presentation">
    <tr>
        <td align="center" valign="middle">

            <table width="320" cellpadding="0" cellspacing="0" role="presentation"
                   style="background:#ffffff; border-radius:14px; padding:30px;
                          box-shadow:0 10px 30px rgba(0,0,0,0.15); text-align:center;">

                <tr>
                    <td>
                        <h2 style="margin:0; font-family:Arial,sans-serif; color:#111;">
                            Your OTP Code
                        </h2>
                        <p style="font-family:Arial,sans-serif; color:#555;">
                            Use this code in the application
                        </p>
                        <div style="
                            font-size:36px;
                            font-weight:bold;
                            letter-spacing:8px;
                            color:#2563eb;
                            margin-top:20px;">
                            {otp_code}
                            <p style="
                            font-family:Arial,sans-serif;
                            color:#777;
                            font-size:14px;
                            margin-top:16px;">
                            Don't share the code with anyone
                            </p>
                        </div>
                    </td>
                </tr>

            </table>

        </td>
    </tr>
</table>

</body>
</html>
"""


class Saver:
    def __init__(self, page):
        self.page = page
        stored = page.client_storage.get("actions")
        if isinstance(stored, dict):
            self.data = stored
        else:
            self.data = {}

    def save(self, key, value):
        self.data[key] = value
        self.page.client_storage.set("actions", self.data)

    def get(self, key, default=None):
        return self.data.get(key, default)

def app_id():
    mkapp = "65277"
    num_account = ''.join(random.choices('0123456789', k=7))
    return (f"{mkapp}-{num_account}")

DB_URL = "https://bank-my-wallet-default-rtdb.asia-southeast1.firebasedatabase.app/login.json"


def main(page:Page):
    page.title = ("Simple Login")
    page.window.width= 390
    page.window.height =740
    page.window.top=45
    page.window.left=570
    page.theme_mode = ThemeMode.LIGHT
    page.scroll = 'auto'
    #page.vertical_alignment="center" #top - bottom
    page.horizontal_alignment="center" # right - left
    ###### appbar start ######
    page.appbar = AppBar(
        bgcolor=Colors.BLACK,
        color=Colors.WHITE,
        title= Text("Simple Login"),
        center_title=True,
        leading_width=40,
        )
    ######appbar end #######
    
    
    img = Image(
        src="loading.gif",
        width=100,
        height=100,
        fit=ImageFit.CONTAIN)
    
    def message_image(msg):
        alert = AlertDialog(
            content=msg,
            modal=True,
            actions_alignment=MainAxisAlignment.END,
        )
        page.overlay.append(alert)
        alert.open = True
        page.update()
        
    def message(msg):
        def close_dialog(ev):
                alert.open = False
                page.update()
        alert = AlertDialog(
            title=Text(msg),
            actions=[TextButton("Ok", on_click=close_dialog)],
            actions_alignment=MainAxisAlignment.END,
        )
        page.overlay.append(alert)
        alert.open = True
        page.update()
        return
    
       
    ######## Tools start ########
    
    def send_otp_click(e):
        message_image(img)
        page.update()
        time.sleep(1.5)
        if signup_email.value.strip() == "":
            def close_dialog(ev):
                alert.open = False
                page.update()
            alert = AlertDialog(
                title=Text("Write the email correctly"),
                actions=[TextButton("Ok", on_click=close_dialog)],
                actions_alignment=MainAxisAlignment.END,
            )
            page.overlay.append(alert)
            alert.open = True
            page.update()
            return
        
        if signup_name.value == "":
            message("Enter your name")
            page.update()
            return
        
        # إرسال OTP على الإيميل
        email_receiver = signup_email.value
        mkmsg.send_html_mail(os.getenv("EMAIL"), os.getenv("APP_PASSWORD"), "MK", f"Hello {signup_name.value.capitalize()}", html_code, email_receiver)
        message("OTP has been sent to your email")

        # تفعيل انتهاء صلاحية OTP
        def otp_timer():
            global otp_code
            time.sleep(60)  # مدة صلاحية OTP
            otp_code = None


        threading.Thread(target=otp_timer, daemon=True).start()

        # تفعيل عداد إعادة الإرسال
        def start_cooldown():
            send_OTP_btn.disabled = True
            remaining = 60
            while remaining > 0:
                send_OTP_btn.text = f"OTP validity period: {remaining}s"
                page.update()
                time.sleep(1)
                remaining -= 1
            send_OTP_btn.text = "Send OTP"
            send_OTP_btn.disabled = False
            page.update()

        threading.Thread(target=start_cooldown, daemon=True).start()

    
    
    def email_exists(email):
        try:
            r = requests.get(DB_URL)
            if r.status_code != 200:
                return False

            users = r.json()
            if not users or not isinstance(users, dict):
                return False

            for _, data in users.items():
                if isinstance(data, dict) and data.get("email") == email:
                    return True

            return False
        except:
            return False
    
    def add1(e):
        message_image(img)
        page.update()
        time.sleep(1.5)       
        fields = [
            signup_name.value,
            signup_email.value,
            signup_OTP.value,
            signup_phone.value,
            signup_pass.value,
            signup_confirm.value,
        ]

        if any(field.strip() == "" for field in fields):
            def close_dialog(ev):
                alert.open = False
                page.update()
            alert = AlertDialog(
                title=Text("Enter what is required"),
                actions=[TextButton("Ok", on_click=close_dialog)],
                actions_alignment=MainAxisAlignment.END,
            )
            page.overlay.append(alert)
            alert.open = True
            page.update()
            return
        # فحص لو الحساب موجود بالفعل
        if email_exists(signup_email.value):
            def close_dialog(ev):
                alert.open = False
                page.update()
            alert = AlertDialog(
                title=Text("Account already exists"),
                actions=[TextButton("Ok", on_click=close_dialog)],
                actions_alignment=MainAxisAlignment.END,
            )
            page.overlay.append(alert)
            alert.open = True
            page.update()
            return

        
        # 2) فحص الباسورد
        if signup_pass.value != signup_confirm.value:
            def close_dialog(ev):
                alert.open = False
                page.update()
            alert = AlertDialog(
                title=Text("The password not equal"),
                actions=[TextButton("Ok", on_click=close_dialog)],
                actions_alignment=MainAxisAlignment.END,
            )
            page.overlay.append(alert)
            alert.open = True
            page.update()
            return

        # 3) فحص OTP
        if str(signup_OTP.value) != str(otp_code):
            def close_dialog(ev):
                alert.open = False
                page.update()
            alert = AlertDialog(
                title=Text("OTP Wrong"),
                actions=[TextButton("Ok", on_click=close_dialog)],
                actions_alignment=MainAxisAlignment.END,
            )
            page.overlay.append(alert)
            alert.open = True
            page.update()
            return

        # 4) تأكد أن كلمة المرور 8 حروف على الأقل
        if len(signup_pass.value) < 8:
            def close_dialog(ev):
                alert.open = False
                page.update()
            alert = AlertDialog(
                title=Text("Please enter at least 8 characters"),
                actions=[TextButton("Ok", on_click=close_dialog)],
                actions_alignment=MainAxisAlignment.END,
            )
            page.overlay.append(alert)
            alert.open = True
            page.update()
            return
        
        message_image(img)
        page.update()

        # 5) إرسال البيانات للـ Firebase عبر requests
        payload = {
            "name": signup_name.value.capitalize(),
            "phone": signup_phone.value,
            "email": signup_email.value,
            "password1": signup_pass.value,
            "password2": signup_confirm.value,
            "account_id": app_id()
        }

        try:
            r = requests.post(DB_URL, json=payload)
            if r.status_code != 200:
                raise Exception(f"Failed to save user. Status code: {r.status_code}")
            
            signup_name.value = ""
            signup_email.value = ""
            signup_phone.value = ""
            signup_pass.value = ""
            signup_confirm.value = ""
            signup_OTP.value = ""
            page.update()
            message("Account created successfully")
        except Exception as ex:
            def close_dialog(ev):
                alert.open = False
                page.update()
            alert = AlertDialog(
                title=Text("Error saving data"),
                content=Text(str(ex)),
                actions=[TextButton("Ok", on_click=close_dialog)],
                actions_alignment=MainAxisAlignment.END,
            )
            page.overlay.append(alert)
            alert.open = True
            page.update()
            return
            
            
            
    global signup_email
    global signup_OTP
    text = Text("Create account",color=Colors.BLACK,size=45)
    signup_name = TextField(label="Name", color=Colors.BLACK)
    signup_email = TextField(label="E-mail", color=Colors.BLACK)
    signup_phone = TextField(label="Phone number", color=Colors.BLACK)
    signup_pass = TextField(label="Password", password=True, can_reveal_password=True, color=Colors.BLACK)
    signup_confirm = TextField(label="Confirm password", password=True, can_reveal_password=True, color=Colors.BLACK)
    signup_OTP = TextField(label="Enter OTP",width=175,max_length=6,keyboard_type=KeyboardType.NUMBER, color=Colors.BLACK)
    send_OTP_btn = ElevatedButton("Send OTP",width=175,on_click=send_otp_click)
    btn1 = ElevatedButton('Create account', width=225, height=45, on_click=add1)
    edit_btn = IconButton(
        icon=Icons.EDIT,
        tooltip="Edit",
        visible=False
    )
    
    ####### Tools end #######
    
    ###### BOTTOMBAR #######
    page.navigation_bar = CupertinoNavigationBar(
        inactive_color=Colors.BLACK,
        destinations=[
            NavigationBarDestination(icon=Icons.PERSON_ADD, label="Create account"),
        ]
    )
    
    ########### Account ID page ########
    
    
    

    

    #####################################
    page.add(text,
            signup_name,
            signup_email,
            Row ([signup_OTP, send_OTP_btn]),
            signup_phone,
            signup_pass,
            signup_confirm,
            btn1,
            )    
    
    page.update()
app(main)
