
from app import create_app, db


app = create_app()


# # RUNNING ON LOCALHOST
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # Ensure database tables are created
#     app.run(debug=True)





# PRODUCTION ENVIRONMENT
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(host='0.0.0.0', port=8080, debug=True)


