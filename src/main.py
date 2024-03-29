import base64
import hashlib
import json
import os
import secrets
import requests
import pymysql
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import text

mailgun_domain = os.environ.get("MAILGUN_DOMAIN")
mailgun_api_key = os.environ.get("MAILGUN_API_KEY")

# Connection details for your Cloud SQL instance
db_hostname = os.environ.get("DB_HOSTNAME")
db_username = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")
db_database_name = os.environ.get("DB_DATABASE_NAME")
db_mysql_port = os.environ.get("DB_PORT")


def generate_unique_verification_code(username):
    """
    Generates a unique verification code for the given username.

    This function uses the secrets module to generate a cryptographically
    secure random string as the verification code.

    Args:
        username (str): The username of the user for whom to generate the code.

    Returns:
        str: The unique verification code.
    """

    # Securely generate a random string with length 32 (can be adjusted)
    verification_code = secrets.token_urlsafe(32)
    # Combine username (hashed for security) and random string
    combined_string = f"{username}-{hashlib.sha256(username.encode('utf-8')).hexdigest()}"
    # Encode the combined string and verification code for URL safety
    return f"{base64.urlsafe_b64encode(combined_string.encode('utf-8')).decode('utf-8')}/{verification_code}"


def send_verification_email(event, context):
    try:
        # Decode the Pub/Sub message
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        user_data = json.loads(pubsub_message)

        # Extract necessary data from the Pub/Sub message
        first_name = user_data.get('first_name')
        username = user_data.get('username')
        hostname = user_data.get('hostname')
        verification_api = user_data.get('verification_api')

        verification_code = generate_unique_verification_code(username)
        verification_link = f"http://{hostname}:8000/{verification_api}?code={verification_code}"
        company_name = "sourabhk"
        from_email = f"noreply@{company_name}.com"
        subject = f"Welcome to {company_name}! Verify Your Email to Get Started"

        # Plain text version (optional but recommended)
        text_body = f"Welcome {first_name},\n" \
                    f"Thank you for signing up with {company_name}! \n" \
                    f"To verify your email address and unlock all features, please click the link below: \n" \
                    f"{verification_link}"

        # HTML version with call to action button
        html_body = f"""\
          <html>
          <body>
            <p>Welcome {first_name},</p>
            <p>Thank you for signing up with {company_name}! To verify your email address and unlock all features, please click the button below:</p>
            <a href="{verification_link}">Verify Your Email</a>
          </body>
          </html>
          """

        # Send email using Mailgun
        response = requests.post(
            f'https://api.mailgun.net/v3/{mailgun_domain}/messages',
            auth=('api', mailgun_api_key),
            data={
                'from': from_email,
                'to': username,
                'subject': subject,
                # 'text': text_body,
                'html': html_body
            }
        )

        if response.status_code == 200:
            print(f'Email sent to {username}')
            engine = connect_tcp_socket()
            track_email(verification_code, username, engine)
        else:
            print(f'Failed to send email: {response.text}')
            # Log error or handle the failure appropriately
    except Exception as e:
        print(f'Error sending email: {e}')
        # Log the error for debugging


def track_email(verification_link, username, engine):
    try:
        with Session(engine) as session:
            # Check if user exists with text() function
            user_query = text(f"SELECT * FROM myapp_user WHERE username = :username")
            user_result = session.execute(user_query, params={'username': username}).fetchone()
            if user_result:
                user_id = user_result[1]
                verification_code = verification_link.split('/')[1]
                insert_query = text("""
                    INSERT INTO myapp_userverification 
                    (user_id, verification_code, sent_at, expires_at, is_used) 
                    VALUES 
                    (:user_id, :verification_code, NOW(), DATE_ADD(NOW(), INTERVAL 2 MINUTE), FALSE)
                """)
                session.execute(insert_query, {'user_id': user_id, 'verification_code': verification_code})
                session.commit()

                print(f'Email sent to {username} tracked with verification code: {verification_code}')
            else:
                print(f'User "{username}" not found in the database.')
    except IntegrityError as e:
        print(f'Error occurred while tracking email (IntegrityError): {e}')
    except Exception as e:
        print(f'Error occurred while tracking email: {e}')


def connect_tcp_socket() -> sqlalchemy.engine.base.Engine:
    try:
        myurl = sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_username,
            password=db_password,
            host=db_hostname,
            port=db_mysql_port,
            database=db_database_name,
        )
        # Create engine
        engine = sqlalchemy.create_engine(
            myurl,
            pool_pre_ping=True
        )
        return engine
    except Exception as e:
        print(f'Error connecting to the database: {e}')
