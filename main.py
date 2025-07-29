from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi import Form
from fastapi.responses import RedirectResponse

import crud

app = FastAPI(title=" Shopping List Manager")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# ------------------- Pydantic Models -------------------

class UserCreate(BaseModel):
    username: str
    email: str

class CategoryCreate(BaseModel):
    category_name: str

class ShoppingListCreate(BaseModel):
    user_id: int
    list_name: str

class ListItemAdd(BaseModel):
    item_id: int
    quantity: float

class QuantityUpdate(BaseModel):
    new_quantity: float

class PurchasedUpdate(BaseModel):
    is_purchased: bool


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    users = crud.get_users()
    return templates.TemplateResponse("index.html", {"request": request, "users": users})

@app.get("/users/{user_id}/lists/view", response_class=HTMLResponse)
def view_user_lists(request: Request, user_id: int):
    user = next((u for u in crud.get_users() if u["user_id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    lists = crud.get_user_shopping_lists(user_id)
    return templates.TemplateResponse("user_lists.html", {
        "request": request,
        "user": user,
        "shopping_lists": lists
    })

@app.get("/lists/{list_id}/view", response_class=HTMLResponse)
def view_list_detail(request: Request, list_id: int):
    # Find the shopping list
    all_users = crud.get_users()
    for user in all_users:
        lists = crud.get_user_shopping_lists(user["user_id"])
        for lst in lists:
            if lst["list_id"] == list_id:
                items = crud.get_list_items(list_id)
                return templates.TemplateResponse("shopping_list_detail.html", {
                    "request": request,
                    "shopping_list": lst,
                    "user": user,
                    "items": items
                })

    raise HTTPException(status_code=404, detail="Shopping list not found")

@app.get("/lists/{list_id}/items/add", response_class=HTMLResponse)
def show_add_item_form(request: Request, list_id: int):
    # Find the shopping list and user
    all_users = crud.get_users()
    for user in all_users:
        lists = crud.get_user_shopping_lists(user["user_id"])
        for lst in lists:
            if lst["list_id"] == list_id:
                items = crud.get_items()
                return templates.TemplateResponse("add_item.html", {
                    "request": request,
                    "shopping_list": lst,
                    "items": items
                })

    raise HTTPException(status_code=404, detail="List not found")

@app.post("/lists/{list_id}/items/add")
def add_item_to_list_form(list_id: int, item_id: int = Form(...), quantity: float = Form(...)):
    success = crud.add_item_to_list(list_id, item_id, quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Error adding item.")
    return RedirectResponse(url=f"/lists/{list_id}/view", status_code=303)

@app.post("/list_items/{list_item_id}/purchased/")
def mark_item_purchased_form(list_item_id: int, is_purchased: str = Form(...)):
    is_purchased_bool = is_purchased.lower() == "true"
    success = crud.mark_list_item_purchased(list_item_id, is_purchased_bool)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update item status.")
    return RedirectResponse(url=f"/lists/{get_list_id_from_item(list_item_id)}/view", status_code=303)

@app.post("/list_items/{list_item_id}/delete/")
def delete_item_form(list_item_id: int):
    list_id = get_list_id_from_item(list_item_id)
    success = crud.delete_list_item(list_item_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete item.")
    return RedirectResponse(url=f"/lists/{list_id}/view", status_code=303)


@app.post("/users/add")
def add_user_form(username: str = Form(...), email: str = Form(...)):
    success = crud.create_user(username, email)
    if not success:
        raise HTTPException(status_code=400, detail="User creation failed.")
    return RedirectResponse(url="/", status_code=303)

@app.post("/users/{user_id}/delete")
def delete_user(user_id: int):
    success = crud.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error deleting user.")
    return RedirectResponse(url="/", status_code=303)

@app.post("/users/{user_id}/lists/add")
def create_list_form(user_id: int, list_name: str = Form(...)):
    success = crud.create_shopping_list(user_id, list_name)
    if not success:
        raise HTTPException(status_code=400, detail="List creation failed.")
    return RedirectResponse(url=f"/users/{user_id}/lists/view", status_code=303)

@app.post("/lists/{list_id}/delete")
def delete_list_form(list_id: int):
    success = crud.delete_shopping_list(list_id)
    if not success:
        raise HTTPException(status_code=400, detail="List deletion failed.")
    # redirect to user_lists page
    return RedirectResponse(url="/", status_code=303)

@app.get("/items/new", response_class=HTMLResponse)
def new_item_form(request: Request):
    categories = crud.get_categories()
    return templates.TemplateResponse("new_item.html", {
        "request": request,
        "categories": categories
    })

@app.post("/items/new")
def create_item_post(
    item_name: str = Form(...),
    unit: str = Form(...),
    category_id: int = Form(...)
):
    success = crud.create_item(item_name, category_id, unit)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create item.")
    return RedirectResponse(url="/items/new", status_code=303)

# ------------------- User Endpoints -------------------

@app.get("/users/")
def get_users():
    users = crud.get_users()
    return users

@app.post("/users/")
def create_user(user: UserCreate):
    success = crud.create_user(user.username, user.email)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists or error occurred.")
    return {"message": "User created successfully."}


# ------------------- Category Endpoints -------------------

@app.get("/categories/")
def get_categories():
    return crud.get_categories()

@app.post("/categories/")
def create_category(category: CategoryCreate):
    success = crud.create_category(category.category_name)
    if not success:
        raise HTTPException(status_code=400, detail="Category already exists or error occurred.")
    return {"message": "Category created successfully."}

# ------------------- Item Models -------------------
class ItemCreate(BaseModel):
    item_name: str
    category_id: int
    unit: str

# ------------------- Item Endpoints -------------------

@app.get("/items/")
def get_items():
    items = crud.get_items()
    return items

@app.post("/items/")
def create_item(item: ItemCreate):
    success = crud.create_item(item.item_name, item.category_id, item.unit)
    if not success:
        raise HTTPException(status_code=400, detail="Error creating item.")
    return {"message": "Item created successfully."}
# ------------------- Shopping List Endpoints -------------------

@app.post("/lists/")
def create_shopping_list(list_data: ShoppingListCreate):
    success = crud.create_shopping_list(list_data.user_id, list_data.list_name)
    if not success:
        raise HTTPException(status_code=400, detail="Error creating shopping list.")
    return {"message": "Shopping list created successfully."}


@app.get("/users/{user_id}/lists/")
def get_user_lists(user_id: int):
    return crud.get_user_shopping_lists(user_id)


@app.get("/lists/{list_id}")
def get_list_by_id(list_id: int):
    lists = crud.get_user_shopping_lists(0)  
    for l in lists:
        if l["list_id"] == list_id:
            return l
    raise HTTPException(status_code=404, detail="List not found.")

@app.get("/lists/")
def get_all_lists():
    all_lists = []
    for user_id in range(1, 10):  
        user_lists = crud.get_user_shopping_lists(user_id)
        all_lists.extend(user_lists)
    return all_lists

@app.delete("/lists/{list_id}")
def delete_list(list_id: int):
    success = crud.delete_shopping_list(list_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error deleting list.")
    return {"message": "Shopping list deleted successfully."}

@app.post("/users/{user_id}/lists/{list_id}/delete")
def delete_list(user_id: int, list_id: int):
    success = crud.delete_shopping_list(list_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error deleting list.")
    return RedirectResponse(url=f"/users/{user_id}/lists/view", status_code=303)

# ------------------- List Item Endpoints -------------------

@app.post("/lists/{list_id}/items/")
def add_item_to_list(list_id: int, list_item: ListItemAdd):
    success = crud.add_item_to_list(list_id, list_item.item_id, list_item.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add item.")
    return {"message": "Item added to list."}


@app.get("/lists/{list_id}/items/")
def get_items_in_list(list_id: int):
    return crud.get_list_items(list_id)


@app.put("/list_items/{list_item_id}/quantity/")
def update_item_quantity(list_item_id: int, data: QuantityUpdate):
    success = crud.update_list_item_quantity(list_item_id, data.new_quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update quantity.")
    return {"message": "Quantity updated."}


@app.put("/list_items/{list_item_id}/purchased/")
def mark_item_purchased(list_item_id: int, data: PurchasedUpdate):
    success = crud.mark_list_item_purchased(list_item_id, data.is_purchased)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update status.")
    return {"message": "Purchased status updated."}


@app.delete("/list_items/{list_item_id}/")
def delete_item_from_list(list_item_id: int):
    success = crud.delete_list_item(list_item_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete item.")
    return {"message": "Item deleted from list."}

# ------------------- helper functions -------------------

def get_list_id_from_item(list_item_id: int) -> int:
    items = []
    for user in crud.get_users():
        for lst in crud.get_user_shopping_lists(user["user_id"]):
            items = crud.get_list_items(lst["list_id"])
            for item in items:
                if item["list_item_id"] == list_item_id:
                    return lst["list_id"]
    raise HTTPException(status_code=404, detail="Item not found in any list")
