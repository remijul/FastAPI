from fastapi import FastAPI

# Create a FastAPI instance
app = FastAPI(
    title="My First API",
    description="A simple API built with FastAPI",
    version="0.1.0"
)

# Create a root endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Create an endpoint that returns your name
@app.get("/name")
async def get_name():
    return {"name": "Your Name"}

# Create an endpoint that takes a name parameter and returns a greeting
@app.get("/greet/{name}")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}

# Create an endpoint that takes query parameters
@app.get("/query")
async def query_params(name: str = "World", age: int = None):
    response = {"message": f"Hello, {name}!"}
    if age:
        response["age"] = age
    return response