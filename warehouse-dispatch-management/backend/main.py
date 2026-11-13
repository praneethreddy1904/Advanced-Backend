from fastapi import FastAPI, HTTPException, Header, Body
import functions
from fastapi.middleware.cors import CORSMiddleware
from datetime import date

app = FastAPI()
@app.get("/")
def hello():
    return {"message": "Warehouse-Dispatch-Management running successfully"}

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods = ["*"],
    allow_headers = ["*"],

)

# 1 - POST - Register a package
@app.post("/packages", status_code=201)
def add_package(package_name: str, destination: str, weight: float, arrival_date: date, token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    if weight <= 0:
        raise HTTPException(status_code=422, detail="Weight must be greater than 0")
    return functions.add_package(package_name, destination, weight, arrival_date)


# 2 - GET - Get particular package details
@app.get("/packages/{package_id}")
def get_package_details(package_id: int, token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    response = functions.get_package(package_id)
    if response is None:
        raise HTTPException(status_code=404,detail="Package not found")
    return response

# 5 - GET - Search and filter packages
@app.get("/packages")
def search_packages(destination: str, status: str, arrival_date: date, token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return functions.get_all_packages(destination=destination, status=status, arrival_date=arrival_date)

# 3 - patch - Update package details
@app.patch("/packages/{package_id}")
def update_package(package_id: int, package_name: str, destination: str,weight: float, arrival_date: date, status: str, token = Header(None)):    
    username = functions.verify_token(token = token)
    if not username:    
        raise HTTPException(status_code=401, detail="Invalid token")
    if status is not None and status not in ["pending", "dispatched"]:
        raise HTTPException(status_code=422, detail="Invalid status")
    response = functions.update_package(package_id, package_name, destination,weight, arrival_date, status)
    if response is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return response

# 4 - DELETE - Delete package if not dispatched
@app.delete("/packages/{package_id}")
def delete_package(package_id: int, token = Header(None)):
    username = functions.verify_token(token = token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    response = functions.delete_package(package_id)
    if response == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")
    if response == "dispatched":
        raise HTTPException(status_code=409, detail="Cannot delete a dispatched package")
    return response

# 6 - View dispatch batches (filter by destination, vehicle, dispatch status)
@app.get("/dispatch-batches")
def get_dispatch_batches(destination=None, vehicle=None, status=None, token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or Expired token")
     
    batches = functions.search_dispatch_batches(destination,vehicle,status)

    return batches

# 7 - Get warehouse statistics
@app.get("/warehouse/statistics")
def warehouse_statistics(token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or Expired token")
    statistics = functions.get_warehouse_statistics()
    return statistics


# 8 - Add data manually (e.g. create a dispatch batch and assign packages)
@app.post("/dispatch-batches")
def create_dispatch_batch(
    destination: str = Body(),
    vehicle: str = Body(),
    package_ids: list[int] = Body(),
    token = Header(None)
):
    response = functions.create_dispatch_batch(
        destination,
        vehicle,
        package_ids
    )
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or Expired token")

    if response == "no packages provided":
        raise HTTPException(status_code=400, detail="At least one package is required")

    if response == "duplicate package IDs":
        raise HTTPException(status_code=400, detail="Duplicate package IDs are not allowed")

    if response == "package not found":
        raise HTTPException(status_code=404, detail="One or more packages not found")

    if response == "destination mismatch":
        raise HTTPException(status_code=400, detail="All packages must have the same destination as the batch")

    if response == "package already assigned or dispatched":
        raise HTTPException(status_code=400, detail="One or more packages are already assigned or dispatched")

    return response

# ---------------------------------
@app.post("/register")
def register_user(user_name = Body(), password = Body()):
    if functions.register_user(user_name=user_name, password=password):
        return {"message": "user registered successfully"}
    return HTTPException(status_code=400, detail="User already exists")


@app.post("/login")
def login(username = Body(), password=Body()):
    token = functions.verify_login(username=username, password=password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token


@app.post("/refresh")
def refresh_token(refresh_token = Header(None)):
    username = functions.verify_login(refresh_token=refresh_token, token_type="refresh")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = functions.create_token(username=username, token_type="access")
    return {"access_token": access_token}


