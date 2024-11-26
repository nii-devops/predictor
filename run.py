from app import create_app, db
import json


def lambda_handler(event, context):
    app = create_app()
    return (app,
            event,
            context)










# # RUNNING ON LOCALHOST
# if __name__ == '__main__':
#     app.run(debug=True)





# PRODUCTION ENVIRONMENT
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # Create tables if they don't exist
#     app.run(host='0.0.0.0', port=8080, debug=True)


