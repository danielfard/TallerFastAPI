import openai
import uvicorn
from config.config import Config
from config.database import Base, Session, engine
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from models.fruits import Fruit as FruitModel
from schemas.fruits import Fruit, ListFruits, UpdateFruit
from schemas.openai import OpenAISchema

app = FastAPI()
tabla_frutas = []

Base.metadata.create_all(bind=engine)


@app.post("/aplicar_openai", status_code=status.HTTP_200_OK, tags=["OpenAI"])
def openai_aplication(pregunta: OpenAISchema):
    openai.api_key = Config.API_KEY_OPEN_IA

    response = openai.Completion.create(
        engine="text-davinci-002", prompt=pregunta.question, max_tokens=60
    )
    message = response.choices[0].text.strip()

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": message})


@app.get(
    "/all_fruits",
    status_code=status.HTTP_200_OK,
    response_model=ListFruits,
    tags=["Fruits"],
)
def get_all_fruits():
    """
    ## Response
        - fruits: List(Fruit)
    """
    db = Session()
    result = db.query(FruitModel).all()

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=jsonable_encoder(result)
    )


@app.get("/{id}", status_code=status.HTTP_200_OK, tags=["Fruits"], response_model=Fruit)
def get_a_fruit(id: int):
    db = Session()
    result = db.query(FruitModel).filter(FruitModel.id == id).first()
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No se encontro una fruta con ese id"},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=jsonable_encoder(result)
    )


@app.post(
    "/create_fruit",
    status_code=status.HTTP_201_CREATED,
    response_model=Fruit,
    summary="Este endpoint me crea una fruta",
    tags=["Fruits"],
)
def create_fruit(fruit: Fruit):
    """
    ## Args
        - fruit: Fruit
    ## Response
        - fruit: Fruit

    """
    db = Session()
    new_fruit = FruitModel(**fruit.dict())
    db.add(new_fruit)
    db.commit()
    return fruit.dict()


@app.delete("/{id}", status_code=status.HTTP_200_OK, tags=["Fruits"])
def delete_fruit(id: int):
    db = Session()
    result = db.query(FruitModel).filter(FruitModel.id == id).first()
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No se encontro una fruta con ese id para eliminar"},
        )

    result_return = result
    db.delete(result)
    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=jsonable_encoder(result_return)
    )


@app.patch("/{id}", status_code=status.HTTP_200_OK, tags=["Fruits"])
def update_fruit(fruit: UpdateFruit):
    db = Session()
    result = db.query(FruitModel).filter(FruitModel.id == fruit.id).first()
    if not result:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No se encontro una fruta con ese id para actualizar"},
        )
    fruit_data = fruit.dict(exclude_unset=True)
    for key, value in fruit_data.items():
        setattr(result, key, value)

    result_return = result
    db.add(result)
    db.commit()
    db.refresh(result)

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=jsonable_encoder(result_return)
    )


@app.get("/", status_code=status.HTTP_302_FOUND, include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
