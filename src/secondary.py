from fastapi import FastAPI, Body

app = FastAPI()
port = 5040

msg_store = list()


@app.put('/append')
async def append(msg: str = Body(..., title="msg", embed=True)):
    try:
        msg_store.append(msg)
        print(f"Successfully added msg {msg}")
        return {'status': 'ok'}
    except Exception as err:
        print(f"Adding failed. There was the following error: {err}")
        return {'status': 'false'}


@app.get('/list')
async def list_messages():
    return {'status': 'ok', 'list': f"{', '.join(msg_store)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=port)
