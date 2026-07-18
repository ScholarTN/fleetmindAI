from typing import List

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.truck import (
    TruckCreate,
    TruckResponse,
    TruckUpdate,
)
from app.services.truck import truck_service

router = APIRouter(
    prefix="/trucks",
    tags=["Trucks"],
)


@router.post(
    "",
    response_model=TruckResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_truck(
    truck: TruckCreate,
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.create_truck(
        db,
        truck,
    )


@router.get(
    "",
    response_model=List[TruckResponse],
)
async def list_trucks(
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.list_trucks(db)


@router.get(
    "/{truck_id}",
    response_model=TruckResponse,
)
async def get_truck(
    truck_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.get_truck(
        db,
        truck_id,
    )


@router.patch(
    "/{truck_id}",
    response_model=TruckResponse,
)
async def update_truck(
    truck_id: str,
    truck: TruckUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await truck_service.update_truck(
        db,
        truck_id,
        truck,
    )


@router.delete(
    "/{truck_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_truck(
    truck_id: str,
    db: AsyncSession = Depends(get_db),
):
    await truck_service.delete_truck(
        db,
        truck_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)