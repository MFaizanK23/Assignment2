from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calorie.db'  # SQLite database file path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Calorie(db.Model):    #db
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    day = db.Column(db.String(50))
    calories = db.Column(db.Integer)

with app.app_context():
    db.create_all()

def getCaljson(**kwargs):   #jsonify the list of data
    calorie_queryset = list(Calorie.query.filter_by(**kwargs))

    return jsonify([{
        "user_id": calorie.user_id,
        "day": calorie.day,
        "calories": calorie.calories
    }for calorie in calorie_queryset])

@app.route("/get-calCount", methods=["GET"]) # root GET request for when the user wants to see all data 
def main():
    response_data = getCaljson()
    return response_data, 200
    
@app.route("/get-calCount/<user_id>", methods=["GET"]) # GET request for when the user wants to find data by user_id
def get_cal(user_id):
    response_data = getCaljson(user_id = user_id)    
    if response_data.json != []:
        return response_data, 200
    return jsonify({"message": f"Calorie count not found for user: '{user_id}'"}), 404

@app.route("/create-calCount", methods=["POST"])   #creates new row for the calorie data
def create_cal():
    data = request.get_json()
    try:
        if data['user_id'] == "" or data['day'] == "" :
            return jsonify(f"Empty Data Fields Not Allowed"),  400

        new_calorie = Calorie(
            user_id=data['user_id'],
            day=data['day'],
            calories=int(data['calories']) 
            
        )
        db.session.add(new_calorie)
        db.session.commit()
        return jsonify({
            "user_id": new_calorie.user_id,
            "day": new_calorie.day,
            "calories": new_calorie.calories
        }), 201
    except KeyError as e: # error testing for when user tries to enter data with a missing field
        return jsonify(f"Required request field missing: {e}"),  400
    except ValueError as e: # when user enters invalid data type 
        return jsonify(f"Invalid form data: {e}"), 400

@app.route("/delete-calCount/<user_id>", methods=["DELETE"]) #Delete function removed first instance of data enetered by user 
def delete_cal(user_id):
    try:
        calorie = Calorie.query.filter_by(user_id=user_id).first()
        if calorie:
            db.session.delete(calorie)
            db.session.commit()
            return jsonify({"message": f"Calorie entry for user: '{user_id}' deleted successfully"}), 200  #Successful deletion
        return jsonify({"message": f"Calorie entry not found for user: '{user_id}'"}), 404  #Invalid User
    except ValueError: 
        return jsonify({"message": f"Invalid user_id format"}), 400  #invalid data format

def update_calorie(user_id, data): #updates the calorie per dataset
    calorie = Calorie.query.filter_by(user_id=user_id).first()
    if calorie:
        try:
            if 'user_id' in data or 'day' in data:
                return jsonify("Cannot update 'user_id' or 'day' fields"), 400 #if user tried to change other data values besides calorie

            # Update calorie data this cam be entered into raw data in postman under json
            if 'calories' in data:
                calorie.calories = int(data['calories'])

            db.session.commit()
            return jsonify({
                "user_id": calorie.user_id,
                "day": calorie.day,
                "calories": calorie.calories
            }), 200
        except ValueError as e:
            return jsonify(f"Invalid form data: {e}"), 400 #error handling for invalid data entry
    return jsonify({"message": f"Calorie entry not found for user: '{user_id}'"}), 404 

@app.route("/update-calCount/<user_id>", methods=["PUT"])
def update_cal(user_id):
    data = request.get_json()
    return update_calorie(user_id, data)

if __name__ == "__main__":
    app.run(debug=True)
