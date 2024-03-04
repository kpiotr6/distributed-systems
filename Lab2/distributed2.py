from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel
from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse

app=FastAPI( )

polls = []

@app.get("/poll")
async def poll():
    return {"polls": polls}

class PollP(BaseModel):
    question: str
    answers: list[str]

class Poll(PollP):
    poll_id: int

@app.post("/poll")
async def create_poll(poll_val: Poll):
    curr_len = len(polls)
    res = {"poll_id": curr_len,"question":poll_val.question, "answers":poll_val.answers}
    polls.append(res)
    return res


@app.get("/poll/{id}")
async def get_poll_id(id: int):
    for p in polls:
        if p.get("poll_id") == id:
            return p
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)


@app.put("/poll/{id}")
async def put_poll_id(id: int, poll: PollP):
    for i,p in enumerate(polls):
        if p.get("poll_id") == id:
            polls[i] = {"poll_id":id, **poll.dict()}
            return polls[i]
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)
        
@app.delete("/poll/{id}")
async def delete_poll_id(id: int):
    for i,p in enumerate(polls):
        if p.get("poll_id") == id:
            polls.remove(polls[i])
            return JSONResponse(status_code=status.HTTP_202_ACCEPTED)

