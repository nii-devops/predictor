
from app import create_app, db
import random
import string


def generate_secret_key():
    """Generate a random 32-character string."""
    invalid_chars = ['=' ,'#', ";", "'", '"', "(", ")", "[", "]", "{", "}"]

    characters = string.ascii_letters + string.digits + string.punctuation
    secret_key = ""

    while len(secret_key) < 33:
        i = random.choice(characters)
        if i not in invalid_chars:
            secret_key += i  
    # Read existing lines from .env file
    with open('.env', 'r') as env_file:
        lines = env_file.readlines()

    # Check if SECRET_KEY exists and replace it
    with open('.env', 'w') as env_file:
        secret_key_written = False  # Track if the secret key has been written
        for line in lines:
            if line.startswith('SECRET_KEY='):
                env_file.write(f'SECRET_KEY={secret_key}\n')  # Replace the existing key
                secret_key_written = True  # Mark that the key has been written
            else:
                env_file.write(line)  # Write unchanged lines
        
        if not secret_key_written:  # If SECRET_KEY was not found, append it
            env_file.write(f'SECRET_KEY={secret_key}\n')  # Append the new key


generate_secret_key()


app = create_app()



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(debug=True)





# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # Create tables if they don't exist
#     app.run(host='0.0.0.0', port=8080, debug=True)


