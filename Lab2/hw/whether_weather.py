from fastapi import FastAPI,responses
from datetime import date
import coordinates
from weather_services import VisualCrossingService
from weather_services import OpenMeteoService
import asyncio
from enums.InfoTypesEnum import InfoTypesEnum
from tabulate import tabulate
from Exceptions import StatusCodeException
import traceback
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from helpers import  build_response
app = FastAPI()



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc.error), status_code=400)

@app.get("/send",response_class=responses.HTMLResponse)
async def get_form_response(city: str, from_date: date, to_date: date):
    try:
        f_date = str(from_date)
        t_date = str(to_date)
        if t_date < f_date:
            raise StatusCodeException("Initial date is later than final date","",400)
        city = await coordinates.get_cities(city, 1)
        coords = coordinates.extract_coordinates(city[0])
        meteo1 = OpenMeteoService(coords[0], coords[1])
        meteo2 = VisualCrossingService(coords[0], coords[1])
        name = city[0].get("name")
        vals = await asyncio.gather(
            *[meteo1.get_data(f_date, t_date,
                                   [InfoTypesEnum.TEMPERATURE_MIN, InfoTypesEnum.TEMPERATURE_MAX,
                                    InfoTypesEnum.RAIN, InfoTypesEnum.WIND, InfoTypesEnum.DATE],
                             ),meteo2.get_data(f_date, t_date,
                                   [InfoTypesEnum.TEMPERATURE_MIN, InfoTypesEnum.TEMPERATURE_MAX,
                                    InfoTypesEnum.RAIN, InfoTypesEnum.WIND, InfoTypesEnum.DATE],
                             )])
        return build_response(vals,"Open Meteo", "Visual Crossing",name)
    except StatusCodeException as error:
        traceback.print_exc()
        return PlainTextResponse(str(error.code)+" "+str(error),status_code=error.code)
    except Exception as error:
        return PlainTextResponse("500 Internal Server Error "+str(error.args[0]), status_code=500)
@app.get("/", response_class=responses.HTMLResponse)
async def get_form():
    with open("html/form.html") as file:
        return "".join(file.readlines())
