from fastapi import FastAPI, Query
from starlette.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
from typing import Optional
import os

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://codewithperry:uYIoXdcbIBi3qdBh@cluster0.iub7ykj.mongodb.net/",
)
client = MongoClient(MONGO_URI)
db = client["Restaurant"]
userCollection = db["users"]
dishesCollection = db["dishes"]
tablesCollection = db["tables"]
ordersCollection = db["orders"]


# -------------------- Models --------------------
class User(BaseModel):
    name: str
    mail: EmailStr
    password: str


class LoginUser(BaseModel):
    mail: EmailStr
    password: str


class UpdateProfile(BaseModel):
    # Identifier: current email of the user
    mail: EmailStr
    # Optional updates
    name: Optional[str] = None
    new_mail: Optional[EmailStr] = None
    icon: Optional[str] = None
    address: Optional[str] = None


class TableModel(BaseModel):
    table_id: int
    table_type: Optional[str] = None
    seats: int


class TableUpdate(BaseModel):
    table_type: Optional[str] = None
    seats: Optional[int] = None


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    mail: Optional[EmailStr] = None
    address: Optional[str] = None
    icon: Optional[str] = None


# -------------------- Root --------------------
@app.get("/")
def default():
    return {"data": "Hello World"}


# -------------------- Auth --------------------
@app.post("/register")
def register(user: User):
    if userCollection.find_one({"mail": user.mail}):
        return {"response": "alreadyExists"}
    userCollection.insert_one({
        "name": user.name,
        "mail": user.mail,
        "password": user.password,
    })
    return {"response": "success"}


@app.post("/login")
def login(user: LoginUser):
    userInDb = userCollection.find_one({"mail": user.mail})
    if not userInDb:
        return {"response": "notExist"}
    if userInDb["password"] == user.password:
        userInDb["_id"] = str(userInDb["_id"])
        userInDb.pop("password", None)
        return {"response": "success", "user": userInDb}
    return {"response": "wrongPassword"}


# -------------------- Profile --------------------
@app.put("/update_profile")
def update_profile(update: UpdateProfile):
    update_fields = {}
    if update.name is not None:
        update_fields["name"] = update.name
    if update.icon is not None:
        update_fields["icon"] = update.icon
    if update.address is not None:
        update_fields["address"] = update.address
    # Handle email change
    if update.new_mail is not None and update.new_mail != update.mail:
        # prevent duplicates
        if userCollection.find_one({"mail": update.new_mail}):
            return {"response": "alreadyExists"}
        update_fields["mail"] = update.new_mail
    if not update_fields:
        return {"response": "no_update_fields"}
    result = userCollection.update_one(
        {"mail": update.mail}, {"$set": update_fields}
    )
    if result.matched_count == 0:
        return {"response": "user_not_found"}
    return {"response": "success"}


@app.get("/profile")
def get_profile(id: str = Query(None), mail: str = Query(None)):
    query = {}
    if id:
        from bson import ObjectId
        try:
            query["_id"] = ObjectId(id)
        except Exception:
            return {"response": "invalid_id"}
    elif mail:
        query["mail"] = mail
    else:
        return {"response": "missing_param"}
    user = userCollection.find_one(query)
    if not user:
        return {"response": "not_found"}
    user["_id"] = str(user["_id"])
    user.pop("password", None)
    user["email"] = user.get("mail", "")
    return {"response": "success", "user": user}


# -------------------- Admin Users --------------------
@app.get("/users")
def get_users():
    users = []
    cursor = userCollection.find({})
    for u in cursor:
        u["_id"] = str(u["_id"])
        u.pop("password", None)
        users.append(u)
    return {"response": "success", "users": users}


@app.put("/users/{user_id}")
def admin_update_user(user_id: str, update: AdminUserUpdate):
    from bson import ObjectId
    try:
        oid = ObjectId(user_id)
    except Exception:
        return {"response": "invalid_id"}
    update_fields = {}
    if update.name is not None:
        update_fields["name"] = update.name
    if update.address is not None:
        update_fields["address"] = update.address
    if update.icon is not None:
        update_fields["icon"] = update.icon
    if update.mail is not None:
        existing = userCollection.find_one({"mail": update.mail, "_id": {"$ne": oid}})
        if existing:
            return {"response": "alreadyExists"}
        update_fields["mail"] = update.mail
    if not update_fields:
        return {"response": "no_update_fields"}
    result = userCollection.update_one({"_id": oid}, {"$set": update_fields})
    if result.matched_count == 0:
        return {"response": "not_found"}
    return {"response": "success"}


@app.delete("/users/{user_id}")
def admin_delete_user(user_id: str):
    from bson import ObjectId
    try:
        oid = ObjectId(user_id)
    except Exception:
        return {"response": "invalid_id"}
    result = userCollection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return {"response": "not_found"}
    return {"response": "success"}


# -------------------- Dishes --------------------
@app.get("/dishes")
def dishes():
    dishes_list = []
    cursor = dishesCollection.find({})
    for d in cursor:
        d["_id"] = str(d["_id"])
        dishes_list.append(d)
    return {"response": "success", "dishes": dishes_list}


# -------------------- Tables --------------------
@app.post("/tables")
def create_table(table: TableModel):
    if tablesCollection.find_one({"table_id": table.table_id}):
        return {"response": "exists"}
    # Derive type if not provided
    table_type = table.table_type
    if table_type is None:
        if table.seats == 2:
            table_type = "couple"
        elif table.seats == 4:
            table_type = "family"
        else:
            table_type = "custom"
    tablesCollection.insert_one({
        "table_id": table.table_id,
        "table_type": table_type,
        "seats": table.seats,
    })
    return {"response": "success"}

@app.get("/tables")
def get_tables():
    tables = list(tablesCollection.find({}))
    for t in tables:
        t["_id"] = str(t["_id"])
    return {"response": "success", "tables": tables}


@app.put("/tables/{table_id}")
def update_table(table_id: int, update: TableUpdate):
    updates = {}
    if update.seats is not None:
        updates["seats"] = update.seats
        # If type not explicitly provided, derive from seats to keep consistency
        if update.table_type is None:
            if update.seats == 2:
                updates["table_type"] = "couple"
            elif update.seats == 4:
                updates["table_type"] = "family"
            else:
                updates["table_type"] = "custom"
    if update.table_type is not None:
        updates["table_type"] = update.table_type
    if not updates:
        return {"response": "no_update_fields"}
    result = tablesCollection.update_one({"table_id": table_id}, {"$set": updates})
    if result.matched_count == 0:
        return {"response": "not_found"}
    return {"response": "success"}


@app.delete("/tables/{table_id}")
def delete_table(table_id: int):
    result = tablesCollection.delete_one({"table_id": table_id})
    if result.deleted_count == 0:
        return {"response": "not_found"}
    return {"response": "success"}


# -------------------- Stats --------------------
@app.get("/stats")
def stats():
    try:
        users_count = userCollection.count_documents({})
    except Exception:
        users_count = 0
    try:
        tables_count = tablesCollection.count_documents({})
    except Exception:
        tables_count = 0
    try:
        orders_count = ordersCollection.count_documents({})
    except Exception:
        orders_count = 0
    return {
        "response": "success",
        "users": users_count,
        "tables": tables_count,
        "orders": orders_count,
    }