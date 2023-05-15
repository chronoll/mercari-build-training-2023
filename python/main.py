import os
import logging
import pathlib
import json
import hashlib
import shutil
from fastapi import FastAPI, Form, HTTPException,UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

items_dict={"items":[]}

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
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
    
    hash=hashlib.sha256()
    hash.update(original_image)
    return hash.hexdigest()

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...),category:str=Form(),image:UploadFile=Form(...)):
    print(name,category,image)
    original_image_path=image.filename
    hashed_str=str(hash_image(original_image_path))
    jpg_name=hashed_str+'.jpg'
    shutil.copy(images/original_image_path, images/jpg_name)
    new_item={"name":name,"category":category,"image":hashed_str}
    items_dict["items"].append(new_item)
    with open("items.json",'w')as f:
        json.dump(items_dict,f)
    logger.info(f"Receive item: {name}")
    return {"message": f"item received: {type(image)}"}

@app.get("/items")
def get_all_item():
    return items_dict

@app.get("/items/{item_id}")
def get_one_item(item_id:int):
    return items_dict["items"][item_id-1]

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


