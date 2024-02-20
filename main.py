from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from prometheus_client import make_asgi_app, Counter, Gauge, Histogram
from models import Package
import random
import uuid
import json
import asyncio
from pydantic import BaseModel, Field
from typing import List, Dict
import time

class Dimension(BaseModel):
    width: float
    height: float
    length: float

class PackageInTruck(BaseModel):
    package_id: str

class Truck(BaseModel):
    truck_id: str = Field(alias='id')
    truck_capacity: Dimension
    max_weight: float
    packages: List[PackageInTruck]

class Delivery(BaseModel):
    truck_id: str
    travel_time: float = 0.0
    departure_timestamp: float

trucks: Dict[str, Truck] = {}
deliveries: List[Delivery] = []

app = FastAPI()

# Metrics
packages_counter = Counter("packages_counter", "Number of packages sent")
trucks_gauge = Gauge("trucks_gauge", "Number of trucks in delivery")  
package_delivery_time = Histogram("package_delivery_time", "Time taken to deliver a package")
packages_per_truck = Histogram("packages_per_truck", "Number of packages per truck")
packages_waiting_for_delivery = Gauge("packages_waiting_for_delivery", "Number of packages waiting for delivery")

async def generate_packages():
    while True:
        await asyncio.sleep(1)
        package = Package(width=random.uniform(1.0, 100.0),
                          height=random.uniform(1.0, 100.0),
                          length=random.uniform(1.0, 100.0),
                          package_id=str(uuid.uuid4()))
        packages_counter.inc()
        yield f"data: {json.dumps(package.model_dump())}\n\n".encode('utf-8')

@app.get("/packages")
async def stream_packages():
    return StreamingResponse(generate_packages(), media_type="text/event-stream")

@app.post("/trucks")
async def add_truck(truck: Truck):
    trucks[truck.truck_id] = truck
    travel_time = random.uniform(0.0, 24.0)
    deliveries.append(Delivery(truck_id=truck.truck_id, travel_time=travel_time, timestamp=time.time()))
    trucks_gauge.set(len(trucks))
    packages_per_truck.observe(len(truck.packages))
    return {"message": "Truck added successfully", "truck_id": truck.truck_id}

@app.get("/trucks")
async def get_trucks():
    return trucks

@app.get("/updates")
async def stream_updates():
    async def updates_generator():
        while True:
            await asyncio.sleep(1)
            current_time = time.time()
            overdue_deliveries = [delivery for delivery in deliveries if current_time - (delivery.departure_timestamp + delivery.travel_time) >= 0]
            for delivery in overdue_deliveries:
                yield f"data: {json.dumps({'TruckArrived': delivery.truck_id})}\n\n".encode('utf-8')
                deliveries.remove(delivery)
    return StreamingResponse(updates_generator(), media_type="text/event-stream")

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)