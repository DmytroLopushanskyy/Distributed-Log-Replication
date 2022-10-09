import httpx
from fastapi import FastAPI, Body

app = FastAPI()
port = 5000

secondary_services = [
    "http://127.0.0.1:5020",
    "http://127.0.0.1:5040"
]

msg_store = list()


@app.put('/append')
async def append(msg: str = Body(..., title="msg", embed=True)):
    try:
        msg_store.append(msg)
        print(f"Successfully added msg {msg}")
    except Exception as err:
        print(f"Adding failed. There was the following error: {err}")
        return {'status': 'false'}

    async with httpx.AsyncClient() as client:
        for dest_url in secondary_services:
            await client.put(f"{dest_url}/append", json={"msg": msg})

    return {'status': 'ok'}


@app.get('/list')
async def list_messages():
    return {'status': 'ok', 'list': f"{', '.join(msg_store)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=port)
