from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel
from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse

app=FastAPI( )

idc = 0
polls = []



@app.get("/poll")
async def poll():
    return {"polls": polls}

class Poll(BaseModel):
    question: str
    answers: dict[str,str]


@app.post("/poll")
async def create_poll(poll_val: Poll):
    global idc
    res = {"poll_id": idc,"question":poll_val.question, "answers":poll_val.answers, "votes":[]}
    idc+=1
    polls.append(res)
    return JSONResponse(status_code=status.HTTP_201_CREATED,content=res)


@app.get("/poll/{id}")
async def get_poll_id(id: int):
    for p in polls:
        if p.get("poll_id") == id:
            return p
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"error":"Poll with given id not found"})


@app.put("/poll/{id}")
async def put_poll_id(id: int, poll: Poll):
    for i,p in enumerate(polls):
        if p.get("poll_id") == id:
            polls[i] = {"poll_id":id, **poll.dict(), "votes":p.get("votes")}
            return polls[i]
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"error":"Poll with given id not found"})
        
@app.delete("/poll/{id}")
async def delete_poll_id(id: int):
    for i,p in enumerate(polls):
        if p.get("poll_id") == id:
            polls.remove(polls[i])
            return JSONResponse(status_code=status.HTTP_202_ACCEPTED,content=polls[i])
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"error":"Poll with given id not found"})

@app.get("/poll/{id}/vote")
async def get_poll_votes(id: int):
    for p in polls:
        if p.get("poll_id")==id:
            return p.get("votes")
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"error":"Poll with given id not found"})

class Answer(BaseModel):
    answer_key: str

@app.post("/poll/{id}/vote")
async def post_poll_vote(id:int, answer: Answer):
    for p in polls:
        if p.get("poll_id")==id:
            if answer.answer_key in p.get("answers").keys():
                curr_max = max(p.get("votes"),key=lambda x: x.get("vote_id"),default=0)+1
                res = {"vote_id":curr_max,"value":answer.answer_key}
                p.get("votes").append(res)
                return JSONResponse(status_code=status.HTTP_201_CREATED,content=res)
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"error":"Answer is out of scope"})
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"error":"Poll with given id not found"})

@app.put("/poll/{id}/vote/{vote_id}")
async def put_poll_vote(id:int,vote_id: int, answer: Answer):
    for p in polls:
        if p.get("poll_id")==id:
            if answer.answer_key in p.get("answers").keys():
                votes = p.get("votes")
                for v in votes:
                    if v.get("vote_id") == vote_id:
                        v.update({"value": answer.answer_key})
                        return v
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"error":"Vote_id not found"})
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"error":"Answer is out of scope"})
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"error":"Poll with given id not found"})    

@app.delete("/poll/{id}/vote/{vote_id}")
async def put_poll_vote(id:int,vote_id: int):
    for p in polls:
        if p.get("poll_id")==id:
            votes = p.get("votes")
            for i,v in enumerate(votes):
                if v.get("vote_id") == vote_id:
                    votes.remove(votes[i])
                    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=votes[i])
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"error":"Vote_id not found"})
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"error":"Poll with given id not found"})    
