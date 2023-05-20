import os
import logging
import pathlib
import json
import hashlib
import shutil
import sqlite3
from fastapi import FastAPI, Form, HTTPException,UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images" #/app/images
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

def hash_image(original_image_path):
    with open(images/original_image_path,'rb')as f:
        original_image=f.read()
    
    hash_=hashlib.sha256()
    hash_.update(original_image)
    return hash_.hexdigest()

def save_to_sql(name,category,jpg_name):
    conn=sqlite3.connect('../db/mercari.sqlite3')
    c=conn.cursor()
    try:
        c.execute("create table items(id integer primary key,name text,category_id integer,image_filename text)")
    except sqlite3.OperationalError:
        pass
    save_schema()
    save_category(category)
    sql="insert into items(name,category_id,image_filename) values (?,?,?)"
    category_id=get_category_id(category)
    c.execute(sql,(name,category_id,jpg_name))
    conn.commit()
    conn.close()

def fetch_all_rows():
    conn=sqlite3.connect('../db/mercari.sqlite3')
    c=conn.cursor()
    c.execute("select * from items")
    sql_data=c.fetchall()
    conn.commit()
    conn.close()
    return format_data(sql_data)

def fetch_rows_by_key(keyword):
    conn=sqlite3.connect('../db/mercari.sqlite3')
    c=conn.cursor()
    sql="select * from items where name=?"
    c.execute(sql,(keyword,))
    sql_data=c.fetchall()
    conn.commit()
    conn.close()
    return format_data(sql_data)

def fetch_rows_by_id(id):
    conn=sqlite3.connect('../db/mercari.sqlite3')
    c=conn.cursor()
    sql="select items.id,items.name,categories.name,image_filename from items inner join categories on items.category_id= categories.id where items.id=?"
    c.execute(sql,(id,))
    sql_data=c.fetchall()
    conn.commit()
    conn.close()
    return format_data(sql_data)

def format_data(sql_data):
    items_dict={"items":[]}
    for item in sql_data:
        dict_for_add={
            "name":item[1],
            "category":item[2],
            "image":item[3]
        }    
        items_dict["items"].append(dict_for_add)
    return items_dict

def get_schema():
    conn=sqlite3.connect('../db/mercari.sqlite3')
    c=conn.cursor()
    c.execute("select * from sqlite_master where type='table' and name='items'")
    schema=c.fetchall()
    conn.commit()
    conn.close()
    return str(schema)

def save_schema():
    conn=sqlite3.connect('../db/items.db')
    c=conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';") 
    tables = c.fetchall()
    if tables: #tableが存在するか判定
        conn.close()
        logger.info("schema has already exited")
        return 
    c.execute('''CREATE TABLE schemas(schema text)''')
    sql="INSERT INTO schemas(schema) VALUES (?)"
    c.execute(sql,(get_schema(),))
    conn.commit()
    conn.close()
    
def save_category(category):
    conn=sqlite3.connect('../db/mercari.sqlite3')
    c=conn.cursor()
    try:
        c.execute("create table categories(id integer primary key,name text unique)")
    except sqlite3.OperationalError:
        pass
    sql="insert into categories(name) values (?)"
    try:
        c.execute(sql,(category,))
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()

def get_category_id(category):
    conn=sqlite3.connect('../db/mercari.sqlite3')
    c=conn.cursor()
    sql="select id from categories where name=?"
    c.execute(sql,(category,))
    category_id=c.fetchall()[0][0]
    conn.commit()
    conn.close()
    return category_id


@app.get("/")
def root():
    return {"message": "Hello, world!"}
    
@app.post("/items")
#def add_item(name: str = Form(...),category:str=Form(),image:UploadFile=Form(...)):
def add_item(name: str = Form(...),category:str=Form(),image:str=Form(...)):
    #original_image_path=image.filename
    original_image_path=image
    hashed_str=str(hash_image(original_image_path))
    jpg_name=hashed_str+'.jpg'
    shutil.copy(images/original_image_path, images/jpg_name)
    save_to_sql(name,category,jpg_name)
    logger.info(f"Receive item: {name}")
    logger.info(f"Receive category: {category}")
    logger.info(f"Receive image:{jpg_name}")
    return {"message": f"item received: {name}"}

@app.get("/items")
def get_all_item():
    return fetch_all_rows()

@app.get("/items/{item_id}")
def get_one_item(item_id:int):
    return fetch_rows_by_id(item_id)

@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.info(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)

@app.get("/search")
def search_name(keyword:str):
    return fetch_rows_by_key(keyword)