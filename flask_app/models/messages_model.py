from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import users_model

class Message():
    def __init__(self, data):
        self.id = data['id']
        self.sender_id = data['sender_id']
        self.recipient_id = data['recipient_id']
        self.message_text = data['message_text']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def get_messages_by_recipient(cls, data):
        query="""SELECT * from users
                    LEFT JOIN messages on users.id = messages.recipient_id
                    LEFT JOIN users as users2 on messages.sender_id = users2.id
                    WHERE users.email= %(email)s
                    ORDER BY messages.created_at desc;"""
        results = connectToMySQL('login_and_registration_schema').query_db(query, data)
        current_user = users_model.User(results[0])
        all_messages = []
        all_messages_from = []

        if not results[0]['messages.id'] == None: 
            for row in results:
                messages_data = {
                    'id': row['messages.id'],
                    'sender_id': row['sender_id'],
                    'recipient_id': row['recipient_id'],
                    'message_text': row['message_text'],
                    'created_at': row['messages.created_at'],
                    'updated_at': row['messages.updated_at']
                }
                all_messages.append(cls(messages_data))
                all_messages_from.append(users_model.User.get_one_by_email({'email':row['users2.email']}))
        current_user.messages_received = all_messages
        current_user.messages_received_from = all_messages_from
        return current_user
    
    @classmethod
    def create_message(cls, data):
        query = "INSERT INTO messages (sender_id,recipient_id,message_text) VALUES (%(sender_id)s,%(recipient_id)s,%(message_text)s);"
        return connectToMySQL('login_and_registration_schema').query_db(query, data)
    
    @classmethod
    def delete_message(cls, data):
        query = "DELETE from messages WHERE id = %(id)s;"
        return connectToMySQL('login_and_registration_schema').query_db(query, data)
    
    @classmethod
    def get_sent_messages(cls,data):
        query = "SELECT * FROM messages where sender_id = %(sender_id)s;"
        results = connectToMySQL('login_and_registration_schema').query_db(query, data)
        sent_messages=[]
        for row in results:
            sent_messages.append(cls(row))
        return sent_messages
        
    
    @staticmethod
    def validate_message(data):
        is_valid=True
        if len(data['message_text'])<5:
            flash("Messages must contain at least 5 characters", "message")
            is_valid=False
        return is_valid
    
