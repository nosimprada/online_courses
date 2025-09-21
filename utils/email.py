from email.message import EmailMessage
from typing import Tuple, Optional

from aiosmtplib import SMTP, SMTPException

from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD

smtp = SMTP(hostname=SMTP_SERVER, port=SMTP_PORT, use_tls=True)


async def send_email(to: str, subject: str, content: str) -> Tuple[bool, Optional[str]]:
    msg = EmailMessage()

    msg["From"] = SMTP_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(content)

    try:
        async with smtp as client:
            await client.login(SMTP_EMAIL, SMTP_PASSWORD)
            result = await client.send_message(msg)

            # Очень большая обработка ошибок для возврата True/False в ответе
            if isinstance(result, dict):
                for receiver, response in result.items():
                    if isinstance(response, tuple) and len(response.count) == 2:
                        status_code, status_message = response
                        success, error = _validate_smtp_response(status_code, status_message, receiver)
                        if not success:
                            return False, error
                    else:
                        if "ok" in str(response).lower() or "queued" in str(response).lower():
                            return True, None
                        else:
                            return False, f"Unexpected response format for {receiver}: {response}"

                return True, None

            elif isinstance(result, tuple):
                if len(result) == 2:
                    status_code, status_message = result
                    success, error = _validate_smtp_response(status_code, status_message, to)
                    if not success:
                        return False, error

                    return True, None
                else:
                    return False, f"Unexpected tuple format: {result}"


            elif isinstance(result, str):
                if "ok" in result.lower() or "queued" in result.lower():
                    return True, None
                else:
                    return False, f"SMTP server returned error: {result}"

            else:
                return False, f"Unexpected return type from send_message: {type(result)} - {result}"

    except SMTPException as e:
        return False, f"SMTP error sending email to {to}: {e}"

    except Exception as e:
        return False, f"Unexpected error sending email to {to}: {e}"


def _validate_smtp_response(status_code, status_message: str, receiver: str) -> Tuple[bool, Optional[str]]:
    if isinstance(status_code, (int, str)):
        try:
            code = int(status_code) if isinstance(status_code, str) else status_code
            if code != 250:
                return False, f"Failed to send to {receiver}: {code} - {status_message}"
        except ValueError:
            if "ok" in str(status_message).lower() or "queued" in str(status_message).lower():
                return True, None
            else:
                return False, f"Failed to send to {receiver}: {status_code} - {status_message}"
    else:
        if "ok" in str(status_message).lower() or "queued" in str(status_message).lower():
            return True, None
        else:
            return False, f"Failed to send to {receiver}: {status_code} - {status_message}"

    return True, None
