import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage
from functools import partial
from typing import Tuple, Optional

from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD

logger = logging.getLogger(__name__)


async def send_course_access_email(
        to: str,
        access_code: str,
        bot_link: str
) -> Tuple[bool, Optional[str]]:
    """Отправляет письмо с кодом доступа к курсу"""
    subject = "Доступ до курсу «Лагідна дисципліна»"

    plain_text = f"""Вітаємо вас! 

Дякуємо, що обрали курс «Лагідна дисципліна».
Тепер у вас є доступ до матеріалів і практик, які допоможуть м'яко, але впевнено вибудовувати підтримку і нові звички у власному житті.

👉 Перехід до курсу відбувається через нашого бота.
Щоб увійти, використайте цей унікальний код доступу:

{access_code}

{bot_link}

Якщо виникнуть будь-які труднощі зі входом чи доступом, ви завжди можете звернутися до підтримки в боті — ми допоможемо.

Дякуємо, що довіряєте нам цей шлях.
Бажаємо вам натхнення й легкості у практиці лагідної дисципліни 🌱

З теплом,
Команда «Лагідна дисципліна»
"""

    html_content = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #4a90e2;">Вітаємо вас!</h2>
    
    <p>Дякуємо, що обрали курс <strong>«Лагідна дисципліна»</strong>.</p>
    
    <p>Тепер у вас є доступ до матеріалів і практик, які допоможуть м'яко, але впевнено вибудовувати підтримку і нові звички у власному житті.</p>
    
    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <p style="font-size: 16px; margin: 0;">👉 Перехід до курсу відбувається через нашого бота.</p>
        <p style="font-size: 16px; margin: 10px 0;">Щоб увійти, використайте цей унікальний код доступу:</p>
        <p style="font-size: 24px; font-weight: bold; color: #4a90e2; text-align: center; margin: 15px 0;">{access_code}</p>
        <p style="text-align: center;">
            <a href="{bot_link}" style="display: inline-block; padding: 12px 24px; background-color: #4a90e2; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Перейти до бота</a>
        </p>
    </div>
    
    <p>Якщо виникнуть будь-які труднощі зі входом чи доступом, ви завжди можете звернутися до підтримки в боті — ми допоможемо.</p>
    
    <p>Дякуємо, що довіряєте нам цей шлях.<br>
    Бажаємо вам натхнення й легкості у практиці лагідної дисципліни 🌱</p>
    
    <p style="color: #888; font-size: 14px; margin-top: 30px;">З теплом,<br>Команда «Лагідна дисципліна»</p>
  </body>
</html>
"""

    logger.info(f"Sending course access email to {to}")
    return await send_email(to, subject, plain_text, html_content)


async def send_email(
        to: str,
        subject: str,
        plain_text: str,
        html_content: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Отправляет email через Gmail SMTP (синхронно в отдельном потоке)
    
    Args:
        to: Email получателя
        subject: Тема письма
        plain_text: Текст письма (plain text)
        html_content: HTML версия письма (опционально)
        
    Returns:
        Tuple[bool, Optional[str]]: (успех, сообщение об ошибке если есть)
    """
    # Запускаем синхронную функцию в отдельном потоке
    loop = asyncio.get_event_loop()
    func = partial(_send_email_sync, to, subject, plain_text, html_content)
    return await loop.run_in_executor(None, func)


def _send_email_sync(
        to: str,
        subject: str,
        plain_text: str,
        html_content: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """Синхронная функция отправки email"""

    # Убираем пробелы из пароля (Gmail может принимать и с пробелами, но на всякий случай)
    app_password = SMTP_PASSWORD.replace(" ", "")

    try:
        # Формируем письмо
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = to
        msg.set_content(plain_text)

        # Добавляем HTML версию если есть
        if html_content:
            msg.add_alternative(html_content, subtype="html")

        logger.info(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")

        # Создаем SSL контекст
        ctx = ssl.create_default_context()

        # Подключаемся по SMTPS (порт 465 с SSL)
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ctx) as smtp:
            logger.info("Connected. Logging in...")
            smtp.login(SMTP_EMAIL, app_password)

            logger.info("Logged in. Sending message...")
            smtp.send_message(msg)

            logger.info(f"✅ Email sent successfully to {to}")

        return True, None

    except smtplib.SMTPAuthenticationError as e:
        error = f"Authentication error: {e}. Check that you're using App Password and 2FA is enabled."
        logger.error(error)
        return False, error

    except smtplib.SMTPException as e:
        error = f"SMTP error: {e}"
        logger.error(error, exc_info=True)
        return False, error
        
    except Exception as e:
        error = f"Unexpected error: {e}"
        logger.error(error, exc_info=True)
        return False, error
