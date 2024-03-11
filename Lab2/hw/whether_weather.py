from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel
from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse

app=FastAPI()