from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from prometheus_client import make_asgi_app, Counter, Gauge, Histogram
# from models import Package
import random
import uuid
import json
import asyncio
from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum
from typing import NamedTuple
from typing import NewType
import time

PackageID = NewType('PackageID', str)
def create_package_id() -> PackageID:
    return PackageID(str(uuid.uuid4()))

class Dimensions(BaseModel):
    width: float
    height: float
    length: float

class PackageType(Enum):
    SMALL = ("Small", Dimensions(width=30.0, height=30.0, length=30.0), 10.0)
    MEDIUM = ("Medium", Dimensions(width=45.0, height=45.0, length=60.0), 20.0)
    LARGE = ("Large", Dimensions(width=60.0, height=60.0, length=40.0), 40.0)
    EXTRA_LARGE = ("Extra Large", Dimensions(width=90.0, height=90.0, length=90.0), 80.0)
    WARDROBE = ("Wardrobe", Dimensions(width=60.0, height=60.0, length=120.0), 40.0)

    def __init__(self, label: str, dimensions: Dimensions, weight_capacity: float):
        self.label = label
        self.dimensions = dimensions
        self.weight_capacity = weight_capacity

    def model_dump(self):
        return {
            "label": self.label,
            "dimensions": self.dimensions.model_dump(),
            "weight_capacity": self.weight_capacity
        }

def create_random() -> PackageType:
    package_types = [PackageType.SMALL, PackageType.MEDIUM, PackageType.LARGE, PackageType.EXTRA_LARGE, PackageType.WARDROBE]
    weights = [50, 25, 10, 10, 5]
    selected_package_type = random.choices(package_types, weights=weights, k=1)[0]

    # Increment the counter for the selected package type
    package_type_counter.labels(package_type=selected_package_type.name).inc()

    return selected_package_type

class Package(BaseModel):
    package_id: PackageID
    package_type: PackageType

    def model_dump(self):
        return {
            "package_id": self.package_id,
            "package_type": self.package_type.model_dump()
        }

class Truck(BaseModel):
    truck_id: str = Field(alias='id')
    truck_capacity: Dimensions
    max_weight: float
    packages: List[PackageID]

class Delivery(BaseModel):
    truck_id: str
    travel_time: float = 0.0
    departure_timestamp: float

trucks: Dict[str, Truck] = {}
deliveries: List[Delivery] = []

app = FastAPI()

# Metrics
packages_counter = Counter("packages_counter", "Number of packages sent")
package_type_counter = Counter('package_creation', 'Number of packages created', ['package_type'])

trucks_gauge = Gauge("trucks_gauge", "Number of trucks in delivery")  
package_delivery_time = Histogram("package_delivery_time", "Time taken to deliver a package")
packages_per_truck = Histogram("packages_per_truck", "Number of packages per truck")
packages_waiting_for_delivery = Gauge("packages_waiting_for_delivery", "Number of packages waiting for delivery")

async def generate_packages():
    while True:
        await asyncio.sleep(random.gauss(0.55, 0.25))
        package = Package(package_id=create_package_id(), package_type=create_random())
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