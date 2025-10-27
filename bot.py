# -*- coding: utf-8 -*-
"""
VPS Hosting Panel Bot - النسخة الاحترافية الكاملة
المطور: Rayen
"""

import os
import json
import subprocess
import threading
import zipfile
from pathlib import Path
import psutil
import platform
import telebot
from datetime import datetime

# ------------------ الإعدادات ------------------
BOT_TOKEN = "7503765926:AAG4iye9Oa5GgRFqwdfTnt8Hu-XZnecBrYU"
OWNER_ID = 6648990053
SERVICE_DIR = "services"
DATA_DIR = "data"
LIBS_DIR = "libs"

# ------------------ تهيئة المجلدات ------------------
for folder in [SERVICE_DIR, DATA_DIR, LIBS_DIR]:
    os.makedirs(folder, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN)

# ------------------ ملفات البيانات ------------------
ADMINS_FILE = Path(DATA_DIR) / "admins.json"
USERS_FILE = Path(DATA_DIR) / "users.json"
BANNED_FILE = Path(DATA_DIR) / "banned.json"
SERVICES_FILE = Path(DATA_DIR) / "services.json"

def load_json(path, default=[]):
    if not path.exists():
        save_json(path, default)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

admins = load_json(ADMINS_FILE, [OWNER_ID])
users = load_json(USERS_FILE, [])
banned = load_json(BANNED_FILE, [])
services = load_json(SERVICES_FILE, [])

# ------------------ أدوات التحقق ------------------
def admin_only(func):
    def wrapper(message, *args, **kwargs):
        if message.from_user.id not in admins:
            bot.reply_to(message, "🚫 فقط الأدمن يمكنه تنفيذ هذا الأمر.")
            return
        return func(message, *args, **kwargs)
    return wrapper

def check_ban(func):
    def wrapper(message, *args, **kwargs):
        if message.from_user.id in banned:
            bot.reply_to(message, "⛔ تم حظرك من استخدام هذا البوت.")
            return
        return func(message, *args, **kwargs)
    return wrapper

# ------------------ أوامر المستخدمين ------------------
@bot.message_handler(commands=["start"])
@check_ban
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    if user_id in admins:
        bot.reply_to(message, f"👑 أهلاً أيها الأدمن {first_name}!")
        return
    if user_id in users:
        bot.reply_to(message, f"✅ مرحبًا {first_name}! يمكنك استخدام /help.")
        return
    bot.reply_to(message, f"🕓 تم إرسال طلبك إلى الأدمن للموافقة، {first_name}.")
    for admin_id in admins:
        bot.send_message(
            admin_id,
            f"📩 طلب جديد من المستخدم: {first_name}\n🆔 ID: `{user_id}`\n\n"
            f"✅ للقبول: /accept {user_id}\n❌ للرفض: /reject {user_id}",
            parse_mode="Markdown"
        )

@bot.message_handler(commands=["accept"])
@admin_only
def accept_user(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id not in users:
            users.append(user_id)
            save_json(USERS_FILE, users)
            bot.reply_to(message, f"✅ تم قبول المستخدم {user_id}.")
            bot.send_message(user_id, "🎉 تم قبولك! يمكنك الآن استخدام /help.")
        else:
            bot.reply_to(message, "⚠️ هذا المستخدم مقبول مسبقًا.")
    except:
        bot.reply_to(message, "❌ استخدم الصيغة: /accept <id>")

@bot.message_handler(commands=["reject"])
@admin_only
def reject_user(message):
    try:
        user_id = int(message.text.split()[1])
        bot.reply_to(message, f"❌ تم رفض المستخدم {user_id}.")
        bot.send_message(user_id, "🚫 تم رفض طلبك من قبل الأدمن.")
    except:
        bot.reply_to(message, "❌ استخدم الصيغة: /reject <id>")

# ------------------ أوامر الأدمن ------------------
@bot.message_handler(commands=["addadmin"])
@admin_only
def add_admin(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id not in admins:
            admins.append(user_id)
            save_json(ADMINS_FILE, admins)
            bot.reply_to(message, f"✅ تمت إضافة الأدمن {user_id}.")
        else:
            bot.reply_to(message, "⚠️ هذا المستخدم أدمن مسبقًا.")
    except:
        bot.reply_to(message, "❌ استخدم الصيغة: /addadmin <id>")

@bot.message_handler(commands=["removeadmin"])
@admin_only
def remove_admin(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id in admins:
            admins.remove(user_id)
            save_json(ADMINS_FILE, admins)
            bot.reply_to(message, f"🛑 تمت إزالة الأدمن {user_id}.")
        else:
        	            bot.reply_to(message, "⚠️ هذا المستخدم ليس أدمن.")
    except:
        bot.reply_to(message, "❌ استخدم الصيغة: /removeadmin <id>")

@bot.message_handler(commands=["ban"])
@admin_only
def ban_user(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id not in banned:
            banned.append(user_id)
            save_json(BANNED_FILE, banned)
            bot.reply_to(message, f"⛔ تم حظر المستخدم {user_id}.")
        else:
            bot.reply_to(message, "⚠️ هذا المستخدم محظور مسبقًا.")
    except:
        bot.reply_to(message, "❌ استخدم الصيغة: /ban <id>")

@bot.message_handler(commands=["unban"])
@admin_only
def unban_user(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id in banned:
            banned.remove(user_id)
            save_json(BANNED_FILE, banned)
            bot.reply_to(message, f"✅ تم رفع الحظر عن المستخدم {user_id}.")
        else:
            bot.reply_to(message, "⚠️ هذا المستخدم ليس محظورًا.")
    except:
        bot.reply_to(message, "❌ استخدم الصيغة: /unban <id>")

# ------------------ أوامر الخدمات ------------------
@bot.message_handler(commands=["upload"])
@admin_only
def upload_service(message):
    msg = bot.reply_to(message, "📦 أرسل اسم الخدمة أولاً:")
    bot.register_next_step_handler(msg, ask_zip_name)

def ask_zip_name(message):
    name = message.text.strip()
    msg = bot.reply_to(message, f"📁 اسم الخدمة: {name}\nالآن أرسل ملف ZIP يحتوي على ملفات الخدمة.")
    bot.register_next_step_handler(msg, handle_zip_upload, name)

def handle_zip_upload(message, name):
    if not message.document or not message.document.file_name.endswith(".zip"):
        bot.reply_to(message, "❌ يجب إرسال ملف ZIP فقط.")
        return
    service_path = Path(SERVICE_DIR) / name
    os.makedirs(service_path, exist_ok=True)
    file_info = bot.get_file(message.document.file_id)
    zip_data = bot.download_file(file_info.file_path)
    zip_path = service_path / f"{name}.zip"
    with open(zip_path, "wb") as f:
        f.write(zip_data)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(service_path)
    venv_path = service_path / "venv"
    subprocess.run(["python3", "-m", "venv", str(venv_path)])
    req_path = service_path / "requirements.txt"
    if req_path.exists():
        bot.reply_to(message, "📦 تثبيت المتطلبات...")
        subprocess.run([str(venv_path / "bin/pip"), "install", "-r", str(req_path)])
    if name not in services:
        services.append(name)
        save_json(SERVICES_FILE, services)
    bot.reply_to(message, f"✅ تم رفع الخدمة {name} بنجاح!")

# ------------------ تشغيل الخدمات ------------------
@bot.message_handler(commands=["run"])
@admin_only
def run_service(message):
    try:
        name = message.text.split()[1]
        path = Path(SERVICE_DIR) / name
        if not path.exists():
            bot.reply_to(message, "❌ الخدمة غير موجودة.")
            return
        venv_python = str(path / "venv/bin/python")
        py_files = list(path.glob("*.py"))
        if not py_files:
            bot.reply_to(message, "⚠️ لا يوجد سكريبتات .py في هذه الخدمة.")
            return
        for py_file in py_files:
            threading.Thread(target=lambda: subprocess.run([venv_python, str(py_file)])).start()
        bot.reply_to(message, f"🚀 تم تشغيل الخدمة {name}.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ أثناء التشغيل: {e}")

# ------------------ الإقلاع ------------------
print("✅ تم تشغيل بوت VPS Hosting Pro Max بنجاح!")
bot.infinity_polling()