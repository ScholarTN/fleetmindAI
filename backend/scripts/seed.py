"""
FleetMind AI — Seed Script
Run with: docker compose exec backend python -m scripts.seed
"""
import asyncio
import random
import uuid
from datetime import datetime, timedelta, date, timezone

from faker import Faker

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.driver import Driver, DriverStatus, DriverAvailability
from app.models.truck import Truck, TruckStatus, FuelType
from app.models.trailer import Trailer, TrailerType, TrailerStatus
from app.models.load import Load, LoadStatus, LoadPriority
from app.models.incident import Incident, IncidentType, IncidentSeverity
from app.services.dispatch import DispatchService
from sqlalchemy import select, func

fake = Faker()

# ── Constants ─────────────────────────────────────────────────────────────────

CITIES = [
    ("Chicago", "IL"), ("Dallas", "TX"), ("Atlanta", "GA"),
    ("Los Angeles", "CA"), ("Memphis", "TN"), ("Houston", "TX"),
    ("Phoenix", "AZ"), ("Denver", "CO"), ("Nashville", "TN"),
    ("Charlotte", "NC"), ("Kansas City", "MO"), ("Columbus", "OH"),
    ("Indianapolis", "IN"), ("Louisville", "KY"), ("St. Louis", "MO"),
    ("Detroit", "MI"), ("Minneapolis", "MN"), ("Seattle", "WA"),
    ("Portland", "OR"), ("Salt Lake City", "UT"), ("El Paso", "TX"),
    ("Albuquerque", "NM"), ("Oklahoma City", "OK"), ("Tulsa", "OK"),
    ("Jacksonville", "FL"),
]

TRUCK_MAKES = {
    "Freightliner": ["Cascadia", "M2 106"],
    "Peterbilt": ["389", "579"],
    "Kenworth": ["T680", "W990"],
    "Volvo": ["VNL 860", "VNL 760"],
    "International": ["LT Series", "RH Series"],
}

COMMODITIES = [
    "General Freight", "Auto Parts", "Electronics", "Food Products",
    "Building Materials", "Paper Products", "Chemicals", "Machinery",
    "Clothing", "Beverages", "Industrial Equipment", "Retail Goods",
    "Pharmaceuticals", "Plastics", "Steel Coils",
]

CUSTOMERS = [
    "Amazon Logistics", "Walmart Supply Chain", "Home Depot",
    "Target Distribution", "Costco Wholesale", "XPO Logistics",
    "C.H. Robinson", "J.B. Hunt", "Schneider National", "Werner Enterprises",
]

INCIDENT_TEMPLATES = [
    (IncidentType.FLAT_TIRE, IncidentSeverity.MEDIUM,
     "Flat tire on I-40 westbound",
     "Driver reported blowout on rear drive axle. Pulled over safely."),
    (IncidentType.BREAKDOWN, IncidentSeverity.HIGH,
     "Engine warning light — loss of power",
     "Driver reported engine fault code and reduced power. Pulled to truck stop."),
    (IncidentType.WEATHER_DELAY, IncidentSeverity.LOW,
     "Winter storm delay on I-70",
     "Heavy snow and ice causing major delays. DOT restricting commercial traffic."),
    (IncidentType.DOT_INSPECTION, IncidentSeverity.LOW,
     "Routine Level 1 DOT inspection",
     "Driver selected for random inspection at weigh station. No violations found."),
    (IncidentType.DETENTION, IncidentSeverity.LOW,
     "Driver detained at shipper over 3 hours",
     "Shipper not ready to load. Driver has been waiting since appointment time."),
    (IncidentType.ACCIDENT, IncidentSeverity.CRITICAL,
     "Minor collision in truck stop parking lot",
     "Driver clipped another trailer while backing. No injuries. Minor damage."),
    (IncidentType.CUSTOMER_DELAY, IncidentSeverity.MEDIUM,
     "Receiver pushed appointment by 6 hours",
     "Customer called to reschedule delivery. Driver holding at nearby truck stop."),
    (IncidentType.TRAFFIC_DELAY, IncidentSeverity.LOW,
     "Major accident on I-95 — 2 hour delay",
     "Multi-vehicle accident blocking all lanes. State police on scene."),
    (IncidentType.DRIVER_ILLNESS, IncidentSeverity.HIGH,
     "Driver reported illness — cannot complete load",
     "Driver called in sick. Load needs to be reassigned immediately."),
    (IncidentType.FUEL_ISSUE, IncidentSeverity.MEDIUM,
     "Fuel card declined at pump",
     "Driver unable to fuel. Fuel card authorization issue. Needs resolution."),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def random_city():
    return random.choice(CITIES)


def random_future_dt(hours_min=2, hours_max=72):
    return datetime.now(timezone.utc) + timedelta(
        hours=random.randint(hours_min, hours_max)
    )


def random_past_dt(hours_min=1, hours_max=168):
    return datetime.now(timezone.utc) - timedelta(
        hours=random.randint(hours_min, hours_max)
    )


async def table_has_data(db, model) -> bool:
    result = await db.execute(select(func.count()).select_from(model))
    return result.scalar_one() > 0


# ── Seeders ───────────────────────────────────────────────────────────────────

async def seed_users(db) -> list[User]:
    print("Creating users...")
    users_data = [
        ("admin@fleetmind.ai", "System Admin", UserRole.ADMIN),
        ("dispatcher1@fleetmind.ai", "Sarah Mitchell", UserRole.DISPATCHER),
        ("dispatcher2@fleetmind.ai", "Marcus Johnson", UserRole.DISPATCHER),
        ("fleetmgr@fleetmind.ai", "Linda Torres", UserRole.FLEET_MANAGER),
        ("safety@fleetmind.ai", "Robert Chen", UserRole.SAFETY_MANAGER),
        ("drivermgr@fleetmind.ai", "James Cooper", UserRole.DRIVER_MANAGER),
    ]
    users = []
    for email, full_name, role in users_data:
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            full_name=full_name,
            hashed_password=hash_password("password123"),
            role=role,
            is_active=True,
        )
        db.add(user)
        users.append(user)
    await db.flush()
    return users


async def seed_drivers(db) -> list[Driver]:
    print("Creating drivers...")
    drivers = []
    statuses = (
        [DriverStatus.DRIVING] * 8 +
        [DriverStatus.ON_DUTY] * 4 +
        [DriverStatus.OFF_DUTY] * 8 +
        [DriverStatus.SLEEPER] * 3 +
        [DriverStatus.AVAILABLE] * 2
    )
    for i in range(25):
        hos_drive = round(random.uniform(1.5, 11.0), 1)
        hos_duty = round(min(hos_drive + random.uniform(0, 3), 14.0), 1)
        if hos_drive >= 4:
            avail = DriverAvailability.AVAILABLE
        elif hos_drive >= 1:
            avail = DriverAvailability.LIMITED
        else:
            avail = DriverAvailability.UNAVAILABLE

        first = fake.first_name()
        last = fake.last_name()
        city, state = random_city()

        driver = Driver(
            id=str(uuid.uuid4()),
            first_name=first,
            last_name=last,
            email=f"{first.lower()}.{last.lower()}{i}@fleetdriver.com",
            phone=fake.numerify("###-###-####"),
            cdl_number=f"CDL{fake.bothify('########').upper()}",
            cdl_expiry=date.today() + timedelta(days=random.randint(90, 1500)),
            date_of_hire=date.today() - timedelta(days=random.randint(90, 3000)),
            home_base=f"{city}, {state}",
            current_location=f"{city}, {state}",
            status=statuses[i],
            availability=avail,
            hos_drive_remaining=hos_drive,
            hos_duty_remaining=hos_duty,
            hos_cycle_remaining=round(random.uniform(10.0, 70.0), 1),
            hos_last_reset=random_past_dt(24, 168),
            hos_violations=random.randint(0, 2),
            on_time_delivery_rate=round(random.uniform(0.82, 0.99), 2),
            total_miles_ytd=random.randint(30000, 120000),
            safety_score=round(random.uniform(72.0, 100.0), 1),
            detention_hours_mtd=round(random.uniform(0, 18.0), 1),
            is_active=True,
        )
        drivers.append(driver)
        db.add(driver)
    await db.flush()
    return drivers


async def seed_trucks(db) -> list[Truck]:
    print("Creating trucks...")
    trucks = []
    statuses = (
    [TruckStatus.AVAILABLE] * 15 +
    [TruckStatus.MAINTENANCE] * 7 +
    [TruckStatus.OUT_OF_SERVICE] * 3

    )
    for i in range(25):
        make = random.choice(list(TRUCK_MAKES.keys()))
        model = random.choice(TRUCK_MAKES[make])
        city, state = random_city()
        truck = Truck(
            id=str(uuid.uuid4()),
            truck_number=f"T-{1001 + i}",
            vin=fake.bothify("?????????????????").upper(),
            license_plate=fake.bothify("???####").upper(),
            make=make,
            model=model,
            year=random.randint(2018, 2024),
            fuel_type=random.choice([FuelType.DIESEL, FuelType.DIESEL, FuelType.HYBRID]),
            status=statuses[i],
            mileage=random.randint(50000, 650000),
            fuel_level=round(random.uniform(0.2, 1.0), 2),
            current_location=f"{city}, {state}",
            current_lat=round(random.uniform(25.0, 49.0), 4),
            current_lon=round(random.uniform(-120.0, -70.0), 4),
            last_service_date=date.today() - timedelta(days=random.randint(10, 90)),
            next_service_date=date.today() + timedelta(days=random.randint(10, 180)),
            is_active=True,
        )
        trucks.append(truck)
        db.add(truck)
    await db.flush()
    return trucks


async def seed_trailers(db) -> list[Trailer]:
    print("Creating trailers...")
    trailers = []
    types = (
        [TrailerType.DRY_VAN] * 12 +
        [TrailerType.REEFER] * 6 +
        [TrailerType.FLATBED] * 4 +
        [TrailerType.STEP_DECK] * 2 +
        [TrailerType.TANKER] * 1
    )
    statuses = (
        [TrailerStatus.AVAILABLE] * 14 +
        [TrailerStatus.IN_USE] * 8 +
        [TrailerStatus.MAINTENANCE] * 2 +
        [TrailerStatus.OUT_OF_SERVICE] * 1
    )
    for i in range(25):
        city, state = random_city()
        trailer = Trailer(
            id=str(uuid.uuid4()),
            trailer_number=f"TR-{2001 + i}",
            trailer_type=types[i],
            length_ft=53 if types[i] != TrailerType.STEP_DECK else 48,
            capacity_lbs=random.choice([42000, 44000, 45000]),
            status=statuses[i],
            current_location=f"{city}, {state}",
            is_active=True,
        )
        trailers.append(trailer)
        db.add(trailer)
    await db.flush()
    return trailers


async def seed_loads(db) -> list[Load]:
    print("Creating loads...")
    loads = []
    statuses = (
        [LoadStatus.PENDING] * 15 +
        [LoadStatus.ASSIGNED] * 5 +
        [LoadStatus.IN_TRANSIT] * 8 +
        [LoadStatus.DELIVERED] * 10 +
        [LoadStatus.CANCELLED] * 2
    )
    priorities = (
        [LoadPriority.NORMAL] * 20 +
        [LoadPriority.HIGH] * 10 +
        [LoadPriority.CRITICAL] * 5 +
        [LoadPriority.LOW] * 5
    )
    for i in range(40):
        origin = random_city()
        dest = random.choice([c for c in CITIES if c != origin])
        pickup_dt = random_future_dt(2, 48)
        delivery_dt = pickup_dt + timedelta(hours=random.randint(8, 72))

        load = Load(
            id=str(uuid.uuid4()),
            load_number=f"FM-{100000 + i}",
            origin_city=origin[0],
            origin_state=origin[1],
            origin_address=fake.street_address(),
            dest_city=dest[0],
            dest_state=dest[1],
            dest_address=fake.street_address(),
            estimated_miles=random.randint(200, 2200),
            pickup_appointment=pickup_dt,
            delivery_appointment=delivery_dt,
            commodity=random.choice(COMMODITIES),
            weight_lbs=random.randint(8000, 44000),
            trailer_type_required=random.choice([
                TrailerType.DRY_VAN, TrailerType.DRY_VAN,
                TrailerType.REEFER, TrailerType.FLATBED,
            ]),
            status=statuses[i],
            priority=priorities[i],
            customer_name=random.choice(CUSTOMERS),
            customer_reference=f"PO-{fake.bothify('######')}",
            rate_usd=round(random.uniform(1200, 6500), 2),
        )
        loads.append(load)
        db.add(load)
    await db.flush()
    return loads


async def seed_incidents(db, drivers, loads) -> None:
    print("Creating incidents...")
    for i, (itype, severity, title, description) in enumerate(INCIDENT_TEMPLATES):
        driver = random.choice(drivers)
        load = random.choice(loads)
        is_resolved = random.choice([True, False])
        incident = Incident(
            id=str(uuid.uuid4()),
            incident_number=f"INC-{str(uuid.uuid4())[:8].upper()}",
            incident_type=itype,
            severity=severity,
            title=title,
            description=description,
            location=f"{random_city()[0]}, {random_city()[1]}",
            driver_id=driver.id,
            load_id=load.id,
            is_resolved=is_resolved,
            resolved_at=random_past_dt(1, 24) if is_resolved else None,
            resolution_notes="Issue resolved by operations team." if is_resolved else None,
            occurred_at=random_past_dt(1, 72),
        )
        db.add(incident)
    await db.flush()


async def dispatch_loads(db, drivers, trucks, trailers, loads) -> None:
    print("Dispatching loads...")
    dispatch = DispatchService(db)

    available_drivers = [
        d for d in drivers
        if d.availability == DriverAvailability.AVAILABLE
        and d.hos_drive_remaining >= 1.0
    ]
    available_trucks = [
        t for t in trucks
        if t.status == TruckStatus.AVAILABLE
    ]
    available_trailers = [
        t for t in trailers
        if t.status == TrailerStatus.AVAILABLE
    ]
    pending_loads = [
        l for l in loads
        if l.status == LoadStatus.PENDING
    ]

    dispatched = 0
    for load in pending_loads[:15]:
        if not available_drivers or not available_trucks:
            break
        driver = available_drivers.pop(0)
        truck = available_trucks.pop(0)
        trailer = available_trailers.pop(0) if available_trailers else None

        try:
            await dispatch.assign(
                load_id=load.id,
                driver_id=driver.id,
                truck_id=truck.id,
                trailer_id=trailer.id if trailer else None,
            )
            dispatched += 1
        except Exception as e:
            print(f"  Skipped load {load.load_number}: {e}")
            continue

    print(f"  Dispatched {dispatched} loads.")


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    async with AsyncSessionLocal() as db:
        try:
            # Duplicate protection — skip if data exists
            if await table_has_data(db, User):
                print("Database already seeded. Skipping.")
                return

            users = await seed_users(db)
            drivers = await seed_drivers(db)
            trucks = await seed_trucks(db)
            trailers = await seed_trailers(db)
            loads = await seed_loads(db)
            await seed_incidents(db, drivers, loads)
            await dispatch_loads(db, drivers, trucks, trailers, loads)

            await db.commit()
            print("\n✅ Seed complete.")
            print("─" * 40)
            print("Login credentials (all use password123):")
            print("  admin@fleetmind.ai")
            print("  dispatcher1@fleetmind.ai")
            print("  dispatcher2@fleetmind.ai")
            print("  fleetmgr@fleetmind.ai")
            print("  safety@fleetmind.ai")
            print("  drivermgr@fleetmind.ai")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Seed failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())