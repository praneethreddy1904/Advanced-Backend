from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt  # pyright: ignore[reportMissingImports]
from argon2 import PasswordHasher   # pyright: ignore[reportMissingImports]
from argon2.exceptions import VerifyMismatchError   # pyright: ignore[reportMissingImports]

ph = PasswordHasher()

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

USERNAME = "admin"
PASSWORD = "admin123"

ACCESS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

Base = declarative_base()


class Packages(Base):
    __tablename__ = "Packages"
    id = Column(Integer, primary_key=True)
    package_name = Column(String)
    destination = Column(String)
    weight = Column(Float)
    arrival_date = Column(Date)
    status = Column(String, default="pending")


class DispatchBatches(Base):
    __tablename__ = "DispatchBatches"
    id = Column(Integer, primary_key=True)
    vehicle = Column(String)
    destination = Column(String)
    dispatch_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)


class BatchPackages(Base):
    __tablename__ = "BatchPackages"
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("DispatchBatches.id"))
    package_id = Column(Integer, ForeignKey("Packages.id"))


class Users(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    

Base.metadata.create_all(engine)

# 1) add a package
def add_package(package_name, destination, weight, arrival_date):
    session = Session(engine)
    package = Packages(package_name=package_name, destination=destination,weight=weight, arrival_date=arrival_date)
    session.add(package)
    session.commit()
    response = {
        "id": package.id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }
    session.close()
    return response


# 2) get package by id
def get_package_by_id(package_id):
    session = Session(engine)
    package = session.query(Packages).filter(Packages.id == package_id).first()
    if package is not None:
        response = {
                "id": package.id,
                "package_name": package.package_name,
                "destination": package.destination,
                "weight": package.weight,
                "arrival_date": package.arrival_date,
                "status": package.status
        }
    else:
        response = None
    session.close()
    return response

# 3) update package
def update_package(package_id, package_name=None, destination=None, weight=None,arrival_date=None, status=None):
    session = Session(engine)
    package = session.query(Packages).filter(Packages.id == package_id).first()
    if package is None:
        session.close()
        return None
    if package_name is not None:
        package.package_name = package_name
    if destination is not None:
        package.destination = destination
    if weight is not None:
        package.weight = weight
    if arrival_date is not None:
        package.arrival_date = arrival_date
    if status is not None:
            package.status = status
    session.commit()
    response = {
        "id": package.id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }
    session.close()
    return response

# 4) delete package
def delete_package(package_id):
    session = Session(engine)
    package = session.query(Packages).filter(Packages.id == package_id).first()
    if package is None:
        session.close()
        return "not found"
    if package.status == "dispatched":
        session.close()
        return "dispatched"
    response = {
        "id": package.id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": package.arrival_date,
        "status": package.status
    }
    session.delete(package)
    session.commit()
    session.close()
    return response

# 5) search packages
def get_all_packages(destination=None, status=None, arrival_date=None):
    session = Session(engine)
    packages = session.query(Packages)
    if destination is not None:
        packages = packages.filter(Packages.destination == destination)
    if status is not None:
        packages = packages.filter(Packages.status == status)
    if arrival_date is not None:
        packages = packages.filter(Packages.arrival_date == arrival_date)
    response = []
    for package in packages.all():
        response.append({
                "id": package.id,
                "package_name": package.package_name,
                "destination": package.destination,
                "weight": package.weight,
                "arrival_date": package.arrival_date,
                "status": package.status
        })
    session.close()
    return response


# 6) View dispatch batches 
def search_dispatch_batches(destination=None, vehicle=None, status=None):
    session = Session(engine)
    query = session.query(DispatchBatches)
    if destination:
        query = query.filter(DispatchBatches.destination == destination)
    if vehicle:
        query = query.filter(DispatchBatches.vehicle == vehicle)
    if status:
        query = query.filter(DispatchBatches.dispatch_status == status)
    results = []
    for batch in query.all():
        results.append({
            "batch_id": batch.id,
            "destination": batch.destination,
            "vehicle": batch.vehicle,
            "status": batch.dispatch_status
        })
    session.close()
    return results

# 7)Get warehouse statistics
def get_warehouse_statistics():
    session = Session(engine)
    packages = session.query(Packages).all()
    total_received = len(packages)
    pending = 0
    dispatched = 0
    destination_count = {}
    for package in packages:
        if package.status == "pending":
            pending += 1
        if package.status == "dispatched":
            dispatched += 1
        if package.destination:
            destination_count[package.destination] = destination_count.get(package.destination, 0) + 1
    session.close()
    return {
        "total_received": total_received,
        "pending": pending,
        "dispatched": dispatched,
        "destination_wise_count": destination_count
    }

# 8) Add data manually
def create_dispatch_batch(destination, vehicle, package_ids):
    session = Session(engine)
    if len(package_ids) == 0:
        session.close()
        return "no packages provided"
    for package_id in package_ids:
        package = session.query(Packages).filter(Packages.id == package_id).first()
        if package is None:
            session.close()
            return "package not found"
        if package.destination != destination:
            session.close()
            return "destination mismatch"
        if package.status in ["assigned", "dispatched"]:
            session.close()
            return "package already assigned or dispatched"
            
    batch = DispatchBatches(destination=destination,vehicle=vehicle,dispatch_status="planned")
    session.add(batch)
    session.commit()
    
    for package_id in package_ids:
        batch_package = BatchPackages(batch_id=batch.id, package_id=package_id)
        session.add(batch_package)
        package = session.query(Packages).filter(Packages.id == package_id).first()
        package.status = "assigned"
    session.commit()
    
    response = {
        "batch_id": batch.id,
        "destination": batch.destination,
        "vehicle": batch.vehicle,
        "status": batch.dispatch_status,
        "package_ids": package_ids
    }
    session.close()
    return response


#-----------login-----------
def verify_login(username, password):
    session = Session(engine)
    user = session.query(Users).filter_by(user_name = username).first
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    
    except VerifyMismatchError:
        session.close()
        return False
    session.close()
    access_token = create_token(username=username, token_type="access")
    refresh_token = create_token(username=username, token_type="refresh")
    return {"access_token": access_token, "refresh_token": refresh_token}

# ----------token-------------
def create_token(username, token_type):
    time = None
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
 
    payload = {
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token
  
def verify_token(token, token_type):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return False
    
    if payload["token_type"] == token_type:
        return payload["username"]
    return False
    

# --------users-----------
def register_user(user_name:str , password:str):
    session = Session(engine)
    user_exists = session.query(Users).filter_by(user_name=user_name).first()
    if user_exists is not None:
        session.close()
        return False
    session.add(Users(user_name=user_name, password=ph.hash(password)))
    session.commit()
    session.close()
    return True


