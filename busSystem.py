from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token


busSys = Flask(__name__)
busSys.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Rohitha_7@localhost/busTrackingSystem'
busSys.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(busSys)
CORS(busSys)

bcrypt = Bcrypt(busSys)
busSys.config['JWT_SECRET_KEY'] = 'Mango123'
jwt = JWTManager(busSys)


# Route table model
class Route(db.Model):
    __tablename__ = 'route'
    route_id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    stops = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "route_id": self.route_id,
            "source": self.source,
            "destination": self.destination,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "stops": self.stops
        }

# Driver table model
class Driver(db.Model):
    __tablename__ = 'driver'
    driver_id = db.Column(db.Integer, primary_key=True)
    driver_name = db.Column(db.String(100), nullable=False)
    driver_phno = db.Column(db.String(15), nullable=False)
    assigned_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "driver_id": self.driver_id,
            "driver_name": self.driver_name,
            "driver_phno": self.driver_phno,
            "assigned_date": str(self.assigned_date)
        }

# Bus table model
class Bus(db.Model):
    __tablename__ = 'bus'
    bus_id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.route_id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.driver_id'), nullable=False)
    bus_num = db.Column(db.String(50), nullable=False)
    bus_type = db.Column(db.String(50), nullable=False)
    current_location = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "bus_id": self.bus_id,
            "route_id": self.route_id,
            "driver_id": self.driver_id,
            "bus_num": self.bus_num,
            "bus_type": self.bus_type,
            "current_location": self.current_location
        }

# User table model
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "email": self.email,
        }

# Bus Pass table model
class BusPass(db.Model):
    __tablename__ = 'bus_pass'
    pass_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    pass_type = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "pass_id": self.pass_id,
            "user_id": self.user_id,
            "issue_date": str(self.issue_date),
            "expiry_date": str(self.expiry_date),
            "pass_type": self.pass_type,
            "status": self.status
        }

# Bus Tracking table model
class BusTracking(db.Model):
    __tablename__ = 'bus_tracking'
    tracking_id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.bus_id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.route_id'), nullable=False)
    current_location = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Numeric(10, 6), nullable=False)
    longitude = db.Column(db.Numeric(10, 6), nullable=False)


    def to_dict(self):
        return {
            "tracking_id": self.tracking_id,
            "bus_id": self.bus_id,
            "route_id": self.route_id,
            "current_location": self.current_location,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude)
        }

# Bus routes
@busSys.route("/addBusDetails", methods=["POST"])
def addBusDetails():
    data = request.json
    new_bus = Bus(
        route_id=data["route_id"],
        driver_id=data["driver_id"],
        bus_num=data["bus_num"],
        bus_type=data["bus_type"],
        current_location=data["current_location"]
    )
    db.session.add(new_bus)
    db.session.commit()
    return jsonify({"Message": "Bus details added successfully", "bus": new_bus.to_dict()})

@busSys.route("/getBusDetails", methods=["GET"])
def getBusDetails():
    buses = Bus.query.all()
    results = [bus.to_dict() for bus in buses]
    return jsonify(results)

@busSys.route("/getBusesByRoute/<int:id>", methods=["GET"])
def getBusesByRoute(id):
    buses = Bus.query.filter(Bus.route_id == id).all()
    if buses:
        results = [bus.to_dict() for bus in buses]
        return jsonify(results)
    else:
        return jsonify({"error": "No buses found for this route"})

@busSys.route("/getBusesByLocation/<int:id>", methods=["GET"])
def getBusesByLocation(id):
    bus = Bus.query.get(id)
    if bus:
        return jsonify({"bus": bus.to_dict()})
    else:
        return jsonify({"error": "No buses found in this location"})

# Route routes
@busSys.route("/addRouteDetails", methods=["POST"])
def addRouteDetails():
    data = request.json
    start_time_format = datetime.strptime(data["start_time"], "%H:%M:%S").time()
    end_time_format = datetime.strptime(data["end_time"], "%H:%M:%S").time()
    
    new_route = Route(
        source=data["source"],
        destination=data["destination"],
        start_time=start_time_format,
        end_time=end_time_format,
        stops=data["stops"]
    )
    db.session.add(new_route)
    db.session.commit()
    return jsonify({"Message": "Route details added successfully", "route": new_route.to_dict()})

@busSys.route("/getRouteDetails", methods=["GET"])
def getRouteDetails():
    routes = Route.query.all()
    results = [route.to_dict() for route in routes]
    return jsonify(results)

# Driver routes
@busSys.route("/addDriverDetails", methods=["POST"])
def addDriverDetails():
    data = request.json
    dateformat = datetime.strptime(data["assigned_date"], "%d/%m/%Y").date()
    
    new_driver = Driver(
        driver_name=data["driver_name"],
        driver_phno=data["driver_phno"],
        assigned_date=dateformat

    )
    db.session.add(new_driver)
    db.session.commit()
    
    return jsonify({
        "Message": "Driver details added successfully",
        "driver": new_driver.to_dict(),
        "bus_id": data.get("bus_id")  # Include bus_id from request if provided
    })

@busSys.route("/getDriverDetails", methods=["GET"])
def getDriverDetails():
    drivers = Driver.query.all()
    results = [driver.to_dict() for driver in drivers]
    return jsonify(results)

# User routes
@busSys.route("/addUser", methods=["POST"])
def addUser():
    data = request.json
    new_user = User(
        user_name=data["user_name"],
        email=data["email"],
        password=data["password"],
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"Message": "User added successfully", "user": new_user.to_dict()})

@busSys.route("/getUsers", methods=["GET"])
def getUsers():
    users = User.query.all()
    results = [user.to_dict() for user in users]
    return jsonify(results)


@busSys.route("/getUser", methods=["GET"])
def getUser():
    # get logged-in user id from session or token
    user_id = get_logged_in_user_id()  # You need to implement this
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict())
    else:
        return jsonify({"error": "User not found"}), 404


@busSys.route("/getUser/<int:user_id>", methods=["GET"])
def getUserById(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"user": user.to_dict()})
    else:
        return jsonify({"error": "User not found"}), 404

@busSys.route("/updateUser/<int:user_id>", methods=["PUT"])
@jwt_required()
def updateUser(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"})
    
    data = request.json
    if 'user_name' in data:
        user.user_name = data['user_name']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    db.session.commit()
    return jsonify({"Message": "User updated successfully", "user": user.to_dict()})

@busSys.route("/deleteUser/<int:user_id>", methods=["DELETE"])
def deleteUser(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"Message": "User deleted successfully"})
    else:
        return jsonify({"error": "User not found"})

# Bus Pass routes
@busSys.route("/addBusPass", methods=["POST"])
def addBusPass():
    data = request.json
    issue_date_format = datetime.strptime(data["issue_date"], "%d/%m/%Y").date()
    expiry_date_format = datetime.strptime(data["expiry_date"], "%d/%m/%Y").date()
    
    new_bus_pass = BusPass(
        user_id=data["user_id"],
        issue_date=issue_date_format,
        expiry_date=expiry_date_format,
        pass_type=data["pass_type"],
        status=data["status"]
    )
    db.session.add(new_bus_pass)
    db.session.commit()
    
    return jsonify({
        "Message": "Bus pass added successfully",
        "bus_pass": new_bus_pass.to_dict()
    })

@busSys.route("/getBusPasses", methods=["GET"])
def getBusPasses():
    bus_passes = BusPass.query.all()
    results = [bus_pass.to_dict() for bus_pass in bus_passes]
    return jsonify(results)

@busSys.route("/getBusPass/<int:pass_id>", methods=["GET"])
def getBusPass(pass_id):
    bus_pass = BusPass.query.get(pass_id)
    if bus_pass:
        return jsonify({"bus_pass": bus_pass.to_dict()})
    else:
        return jsonify({"error": "Bus pass not found"})

@busSys.route("/getBusPassesByUser/<int:user_id>", methods=["GET"])
def getBusPassesByUser(user_id):
    bus_passes = BusPass.query.filter(BusPass.user_id == user_id).all()
    if bus_passes:
        results = [bus_pass.to_dict() for bus_pass in bus_passes]
        return jsonify(results)
    else:
        return jsonify({"error": "No bus passes found for this user"})


# Bus Tracking routes
@busSys.route("/addBusTracking", methods=["POST"])
def addBusTracking():
    data = request.json
    new_tracking = BusTracking(
        bus_id=data["bus_id"],
        route_id=data["route_id"],
        current_location=data["current_location"],
        latitude=data["latitude"],
        longitude=data["longitude"]
    )
    db.session.add(new_tracking)
    db.session.commit()
    return jsonify({"Message": "Bus tracking data added successfully", "tracking": new_tracking.to_dict()})

@busSys.route("/getBusTracking", methods=["GET"])
def getBusTracking():
    tracking_data = BusTracking.query.all()
    results = [tracking.to_dict() for tracking in tracking_data]
    return jsonify(results)

#register route

@busSys.route("/userRegister", methods=["POST"])
def userRegister():
    data = request.json
    username = data.get('username')
    emailid = data.get('emailid')
    password = data.get('password')
    
    if not username or not emailid or not password:
        return jsonify({"error": "Missing credentials"})
    existing_user = User.query.filter_by(email=emailid).first()
    if existing_user:
        return jsonify({"error": "User already exists"})
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        user_name=username,
        email=emailid,
        password=hashed_password,
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"Message": "User Register Success"})

#login route

@busSys.route("/userLogin", methods=["POST"])
def userLogin():
    data = request.json
    emailid = data.get('emailid')
    password = data.get('password')
    
    if not emailid or not password:
        return jsonify({"error": "Missing credentials"})
    user = User.query.filter_by(email=emailid).first()
    
    if not user:
        return jsonify({"Message": "User not found"})

    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(
            identity=user.user_id, 
            expires_delta=timedelta(hours=1)
        )
        return jsonify({
            "Message": "Login Successful",
            "access_token": access_token,
            "user": {
                "user_id": user.user_id,
                "username": user.user_name,
                "emailid": user.email
            }
        })
    else:
        return jsonify({"Message": "Login Failed"})

if __name__ == "__main__":
    with busSys.app_context():
        db.create_all()
    busSys.run(debug=True)