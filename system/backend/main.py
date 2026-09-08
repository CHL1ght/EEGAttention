from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
