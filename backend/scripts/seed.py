"""
Seed script — run with: python -m app.core.seed
Generates realistic logistics data for FleetMind AI development and demos.
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
from app.models.fleet import (
    Truck, Trailer, Load, Incident,
    TruckStatus, TrailerType, LoadStatus, LoadPriority,
    IncidentType, IncidentSeverity,
)

fake = Faker()

TRUCK_MAKES = ["Freightliner", "Peterbilt", "Kenworth", "Volvo", "Mack", "International"]
CITIES = [
    ("Chicago", "IL"), ("Dallas", "TX"), ("Atlanta", "GA"), ("Los Angeles", "CA"),
    ("Memphis", "TN"), ("Houston", "TX"), ("Phoenix", "AZ"), ("Denver", "CO"),
    ("Nashville", "TN"), ("Charlotte", "NC"), ("Kansas City", "MO"), ("Columbus", "OH"),
    ("Indianapolis", "IN"), ("Louisville", "KY"), ("St. Louis", "MO"), ("Detroit", "MI"),
    ("Minneapolis", "MN"), ("Seattle", "WA"), ("Portland", "OR"), ("Salt Lake City", "UT"),
]
COMMODITIES = [
    "General Freight", "Auto Parts", "Electronics", "Food Products", "Building Materials",
    "Paper Products", "Chemicals", "Machinery", "Clothing", "Beverages",
    "Industrial Equipment", "Retail Goods", "Pharmaceuticals", "Plastics",
]
CUSTOMERS = [
    "Amazon", "Walmart", "Home Depot", "Target", "Costco",
    "FedEx Ground", "XPO Logistics", "C.H. Robinson", "J.B. Hunt", "Werner Enterprises",
]


async def seed():
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding FleetMind AI database...")

        # ── Users ─────────────────────────────────────────────────────────────
        users = [
            User(id=str(uuid.uuid4()), email="admin@fleetmind.ai", full_name="Admin User",
                 hashed_password=hash_password("admin123"), role=UserRole.ADMIN),
            User(id=str(uuid.uuid4()), email="dispatcher@fleetmind.ai", full_name="Sarah Mitchell",
                 hashed_password=hash_password("password123"), role=UserRole.DISPATCHER),
            User(id=str(uuid.uuid4()), email="drivermgr@fleetmind.ai", full_name="James Cooper",
                 hashed_password=hash_password("password123"), role=UserRole.DRIVER_MANAGER),
            User(id=str(uuid.uuid4()), email="fleetmgr@fleetmind.ai", full_name="Linda Torres",
                 hashed_password=hash_password("password123"), role=UserRole.FLEET_MANAGER),
            User(id=str(uuid.uuid4()), email="safety@fleetmind.ai", full_name="Robert Chen",
                 hashed_password=hash_password("password123"), role=UserRole.SAFETY_MANAGER),
        ]
        for u in users:
            db.add(u)
        print(f"  ✓ {len(users)} users")

        # ── Trucks ────────────────────────────────────────────────────────────
        trucks = []
        statuses = [TruckStatus.AVAILABLE] * 14 + [TruckStatus.IN_USE] * 8 + [TruckStatus.MAINTENANCE] * 3
        for i, s in enumerate(statuses):
            make = random.choice(TRUCK_MAKES)
            truck = Truck(
                id=str(uuid.uuid4()),
                unit_number=f"T-{1001 + i}",
                make=make,
                model=random.choice(["Cascadia", "389", "T680", "VNL", "Anthem", "LT"]),
                year=random.randint(2018, 2024),
                vin=fake.bothify(text="?????????????????").upper(),
                license_plate=fake.bothify(text="???####"),
                status=s,
                odometer=random.randint(50000, 650000),
                last_service_date=date.today() - timedelta(days=random.randint(10, 90)),
                next_service_miles=random.randint(500000, 750000),
            )
            trucks.append(truck)
            db.add(truck)
        print(f"  ✓ {len(trucks)} trucks")

        # ── Trailers ──────────────────────────────────────────────────────────
        trailers = []
        trailer_types = [TrailerType.DRY_VAN] * 15 + [TrailerType.REEFER] * 6 + \
                        [TrailerType.FLATBED] * 4 + [TrailerType.STEP_DECK] * 2
        for i, tt in enumerate(trailer_types):
            trailer = Trailer(
                id=str(uuid.uuid4()),
                unit_number=f"TR-{2001 + i}",
                trailer_type=tt,
                length_ft=53 if tt != TrailerType.STEP_DECK else 48,
                capacity_lbs=random.choice([44000, 45000, 46000]),
                status=random.choice([TruckStatus.AVAILABLE, TruckStatus.IN_USE]),
            )
            trailers.append(trailer)
            db.add(trailer)
        print(f"  ✓ {len(trailers)} trailers")

        # ── Drivers ───────────────────────────────────────────────────────────
        drivers = []
        available_trucks = [t for t in trucks if t.status == TruckStatus.AVAILABLE]
        driver_statuses = (
            [DriverStatus.DRIVING] * 8 +
            [DriverStatus.ON_DUTY] * 4 +
            [DriverStatus.OFF_DUTY] * 8 +
            [DriverStatus.SLEEPER] * 3
        )
        for i in range(23):
            first = fake.first_name_nonbinary()
            last = fake.last_name()
            hos_drive = round(random.uniform(1.5, 11.0), 1)
            hos_duty = round(hos_drive + random.uniform(0, 3), 1)
            avail = (
                DriverAvailability.AVAILABLE if hos_drive >= 4
                else DriverAvailability.LIMITED if hos_drive >= 1
                else DriverAvailability.UNAVAILABLE
            )
            driver = Driver(
                id=str(uuid.uuid4()),
                first_name=first,
                last_name=last,
                email=f"{first.lower()}.{last.lower()}{i}@xpressdriver.com",
                phone=fake.phone_number()[:15],
                cdl_number=f"CDL{fake.bothify(text='########')}",
                cdl_expiry=date.today() + timedelta(days=random.randint(30, 1500)),
                date_of_hire=date.today() - timedelta(days=random.randint(90, 3000)),
                home_base=random.choice(CITIES)[0] + ", " + random.choice(CITIES)[1],
                current_location=random.choice(CITIES)[0] + ", " + random.choice(CITIES)[1],
                current_lat=round(random.uniform(25.0, 49.0), 4),
                current_lon=round(random.uniform(-120.0, -70.0), 4),
                status=driver_statuses[i],
                availability=avail,
                hos_drive_remaining=hos_drive,
                hos_duty_remaining=min(hos_duty, 14.0),
                hos_cycle_remaining=round(random.uniform(10.0, 70.0), 1),
                hos_violations=random.randint(0, 3),
                on_time_delivery_rate=round(random.uniform(0.82, 0.99), 2),
                total_miles_ytd=random.randint(30000, 120000),
                safety_score=round(random.uniform(72.0, 100.0), 1),
                detention_hours_mtd=round(random.uniform(0, 18.0), 1),
            )
            if i < len(available_trucks) and driver_statuses[i] == DriverStatus.DRIVING:
                truck = available_trucks[i % len(available_trucks)]
                driver.assigned_truck_id = truck.id
                truck.status = TruckStatus.IN_USE
                truck.assigned_driver_id = driver.id

            drivers.append(driver)
            db.add(driver)
        print(f"  ✓ {len(drivers)} drivers")

        # ── Loads ─────────────────────────────────────────────────────────────
        loads = []
        now = datetime.now(timezone.utc)
        load_statuses = (
            [LoadStatus.PENDING] * 10 +
            [LoadStatus.ASSIGNED] * 6 +
            [LoadStatus.IN_TRANSIT] * 8 +
            [LoadStatus.DELIVERED] * 6
        )
        priorities = [LoadPriority.NORMAL] * 18 + [LoadPriority.HIGH] * 6 + [LoadPriority.CRITICAL] * 2 + [LoadPriority.LOW] * 4
        for i in range(30):
            origin = random.choice(CITIES)
            dest = random.choice([c for c in CITIES if c != origin])
            pickup_dt = now + timedelta(hours=random.randint(-24, 48))
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
                trailer_type_required=random.choice([TrailerType.DRY_VAN, TrailerType.DRY_VAN, TrailerType.REEFER, TrailerType.FLATBED]),
                status=load_statuses[i],
                priority=priorities[i],
                customer_name=random.choice(CUSTOMERS),
                customer_reference=f"PO-{fake.bothify(text='######')}",
                rate_usd=round(random.uniform(1200, 6500), 2),
            )
            # Assign drivers to in-transit loads
            if load.status in (LoadStatus.IN_TRANSIT, LoadStatus.ASSIGNED) and drivers:
                driver = random.choice([d for d in drivers if d.status == DriverStatus.DRIVING])
                load.assigned_driver_id = driver.id
                driver.current_load_id = load.id

            loads.append(load)
            db.add(load)
        print(f"  ✓ {len(loads)} loads")

        # ── Incidents ─────────────────────────────────────────────────────────
        incident_templates = [
            (IncidentType.FLAT_TIRE, IncidentSeverity.MEDIUM, "Flat tire on I-40 westbound"),
            (IncidentType.WEATHER_DELAY, IncidentSeverity.LOW, "Weather delay due to heavy fog"),
            (IncidentType.DOT_INSPECTION, IncidentSeverity.LOW, "Routine DOT inspection — Level 1"),
            (IncidentType.DETENTION, IncidentSeverity.LOW, "Driver detained at shipper over 3 hours"),
            (IncidentType.BREAKDOWN, IncidentSeverity.HIGH, "Engine warning light — pulled over safely"),
            (IncidentType.CUSTOMER_DELAY, IncidentSeverity.MEDIUM, "Receiver not ready — appointment pushed 4 hours"),
            (IncidentType.TRAFFIC_DELAY, IncidentSeverity.LOW, "Major accident on I-95 — 2 hour delay estimated"),
            (IncidentType.DRIVER_ILLNESS, IncidentSeverity.HIGH, "Driver reported illness — cannot complete load"),
        ]
        for i, (itype, severity, title) in enumerate(incident_templates):
            driver = random.choice(drivers)
            load = random.choice(loads)
            incident = Incident(
                id=str(uuid.uuid4()),
                incident_number=f"INC-{str(uuid.uuid4())[:8].upper()}",
                incident_type=itype,
                severity=severity,
                title=title,
                description=f"Reported by driver {driver.full_name}. {fake.sentence()}",
                location=random.choice(CITIES)[0],
                driver_id=driver.id,
                load_id=load.id,
                is_resolved=random.choice([True, True, False]),
                occurred_at=now - timedelta(hours=random.randint(1, 72)),
            )
            db.add(incident)
        print(f"  ✓ {len(incident_templates)} incidents")

        await db.commit()
        print("\n✅ Seed complete. Login credentials:")
        print("   admin@fleetmind.ai       / admin123")
        print("   dispatcher@fleetmind.ai  / password123")
        print("   drivermgr@fleetmind.ai   / password123")
        print("   fleetmgr@fleetmind.ai    / password123")
        print("   safety@fleetmind.ai      / password123")


if __name__ == "__main__":
    asyncio.run(seed())
