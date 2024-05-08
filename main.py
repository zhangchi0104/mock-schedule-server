from fastapi import FastAPI, Header, HTTPException
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from random import randint
from faker import Faker
import random
from datetime import datetime, timedelta

app = FastAPI()
fake = Faker()

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

class Date(BaseModel):
    year: int
    month: int
    day: int


class GetScheduleListParam(BaseModel):
    start_date: Date = Field(alias="startDate")
    end_date: Date | None = Field(alias="endDate", default=None)

class IdParam(BaseModel):
    id: str

class GetScheduleListCallParmeters(BaseModel):
    method: Literal["getScheduleList"] = "getScheduleList"
    params: GetScheduleListParam



class HandlerBody(BaseModel):
    method: str
    params: GetScheduleListParam | IdParam

@app.get("/getUserPrmissions")
async def get_user_permissions(auth_token: Annotated[str | None, Header()]):
    if not auth_token:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {"all": True}


@app.post("/handler")
async def handler(body: HandlerBody):
    if body.method == "getScheduleList" and isinstance(body.params, GetScheduleListParam):
        return handle_get_schedule_list(body.params.start_date, body.params.end_date)
    if body.method == "getScheduleDetail" and isinstance(body.params, IdParam):
        return get_schedule_detail(body.params.id)
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")

STATUS_MAPPING = {
    "Schedule.Status.pendingToAccept": "PENDING",
    "Schedule.Status.rejected": "Rejected",
    "Schedule.Status.pendingToStart": "Pneding start",
    "Schedule.Status.checkedin": "Checked in",
    "Schedule.Status.checkedout": "Finished",
}
def handle_get_schedule_list(start_date:Date, end_date: Date | None):
    print(start_date, end_date)
    _start_date = datetime(
        start_date.year,
        start_date.month,
        start_date.day,
    )
    _end_date = datetime(
        end_date.year,
        end_date.month,
        end_date.day,
    ) if end_date else _start_date + timedelta(days=1)
    print(start_date, end_date)
    res = []
    for day in daterange(_start_date, _end_date):
        

        for _ in range(randint(0, 3)):
            item = generateSchedule(day)
            res.append(item)
    return {
        "hasError": False,
        "data": res,
    }


def get_schedule_detail(schedule_id: str):
    day =datetime.today()
    item = generateSchedule(day)
    item["Id"] = schedule_id
    item["Instructions"] = fake.paragraph(5)

    return {
        "hasError": False,
        "data": item,
    }





def generateSchedule(day: datetime): 
    end = day  +  timedelta(hours=23, minutes=59, seconds=59)
    start = fake.date_time_between_dates(datetime_start=day, datetime_end=end)
    status =  random.choice([
                    "Schedule.Status.pendingToAccept",
                    "Schedule.Status.rejected",
                    "Schedule.Status.pendingToStart",
                    "Schedule.Status.checkedin",
                    "Schedule.Status.checkedout"
            ])
    print( "status", status)
    item = {
        "Event": "Personal Care",
        "Carer": {
            "Name": fake.name(),
            "Id": fake.uuid4(),
            "UserId": fake.uuid4(),
        },
        "Customer": {
            "Name": fake.name(),
            "Id": fake.uuid4(),
            "UserId": fake.uuid4(),
        },
        "Clent":{
            "Name": fake.name(),
            "Id": fake.uuid4(),
            "ChargingMethod": "free",
        },
        "Area": {
            "Name": fake.name(),
            "Id": fake.uuid4(),
        },
        "StartUtc": start.isoformat(),
        "EndUtc": fake.date_time_between_dates(datetime_start=start, datetime_end=end).isoformat(),
        
        "Id": fake.uuid4(),
        "Status": status,
        "StatusStr": STATUS_MAPPING[status],
        "CarerProjectId": fake.uuid4(),
        "CustomerProjectId": fake.uuid4(),
    }
    if status in ["Schedule.Status.checkedin", "Schedule.Status.checkedout"]:
        item["CheckinDateTimeUtc"] = fake.date_time_between_dates(datetime_start=start, datetime_end=end).isoformat()
    elif status == "Schedule.Status.checkedout":
        item["CheckoutDateTimeUtc"] = fake.date_time_between_dates(datetime_start=start, datetime_end=end).isoformat()
    if status == "Schedule.Status.pendingToAccept":
        item["ShiftFlag"] = "Pending"
        
    elif status == "Schedule.Status.rejected":
        item["ShiftFlag"] = "Reject"
    else:
        item["ShiftFlag"] = "Accept"

    if status == "Schedule.Status.checkedout":
        item["CanAccept"] = False
        item["CanReject"] = False
        item["CanCheckIn"] = False
        item["CanCheckOut"] = False
    elif status == "Schedule.Status.checkedin":
        item["CanAccept"] = False
        item["CanReject"] = False
        item["CanCheckIn"] = False
        item["CanCheckOut"] = True
    elif status == "Schedule.Status.pendingToStart":
        item["CanAccept"] = False
        item["CanReject"] = False
        item["CanCheckIn"] = True
        item["CanCheckOut"] = False
    elif status == "Schedule.Status.pendingToAccept":
        item["CanAccept"] = True
        item["CanReject"] = True
        item["CanCheckIn"] = False
        item["CanCheckOut"] = False
    elif status == "Schedule.Status.rejected":
        item["CanAccept"] = False
        item["CanReject"] = False
        item["CanCheckIn"] = False
        item["CanCheckOut"] = False
    return item
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
