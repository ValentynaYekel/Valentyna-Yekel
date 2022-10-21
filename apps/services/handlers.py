from apps.core.db import database
from apps.services.models import user_request_exist_view, user_request_list_view, STATUS_MAPPING, UserRequest, \
    user_request_booking_hostel_view, UserRequestReview, hostel_accommodation_view, user_request_details_view
from apps.services.schemas import UserRequestExistenceOut, UserRequestsListOut, CreateUserRequestOut, \
    CreateUserRequestIn, UserRequestBookingHostelOut, CancelRequestOut, CancelRequestIn, UserRequestReviewOut, \
    UserRequestReviewIn, HostelAccomodationViewOut, UserRequestDetailsViewOut
from apps.services.services import create_user_document
from apps.users.handlers import get_current_user
from apps.users.models import UserFaculty

from datetime import datetime
from typing import List
import json

from fastapi import Depends, APIRouter
from sqlalchemy import select, insert, update

router = APIRouter()


@router.get("/{university_id}/user-request-existence/{service_id}/", response_model=UserRequestExistenceOut,
            tags=["Student dashboard"])
async def check_user_request_existence(university_id: int, service_id: int, user=Depends(get_current_user)):
    query = select(user_request_exist_view).where(user_request_exist_view.c.user_id == user.user_id,
                                                  user_request_exist_view.c.university_id == university_id,
                                                  user_request_exist_view.c.service_id == service_id)
    user_request_result = await database.fetch_one(query)
    if user_request_result:
        response = {
            "user_request_id": user_request_result.user_request_id,
            "status": json.loads(user_request_result.status),
            "user_request_exist": True
        }
    else:
        response = {
            "user_request_id": None,
            "status": None,
            "user_request_exist": False
        }
    return response


@router.get("/{university_id}/user-request/", response_model=List[UserRequestsListOut], tags=["Student dashboard"])
async def read_user_request_list(university_id: int, user=Depends(get_current_user)):
    query = select(user_request_list_view).where(user_request_list_view.c.user_id == user.user_id,
                                                 user_request_list_view.c.university_id == university_id)
    return await database.fetch_all(query)


@router.post("/{university_id}/user-request/", response_model=CreateUserRequestOut, tags=["Student dashboard"])
async def create_user_request(university_id: int, user_request: CreateUserRequestIn, user=Depends(get_current_user)):
    query = select(UserFaculty).where(UserFaculty.user_id == user.user_id)
    user_faculty_result = await database.fetch_one(query)
    query = insert(UserRequest).values(date_created=datetime.now(),
                                       comment=user_request.comment,
                                       user_id=user.user_id,
                                       service_id=user_request.service_id,
                                       faculty_id=user_faculty_result.faculty_id,
                                       university_id=university_id,
                                       status_id=STATUS_MAPPING.get("Розглядається"))

    last_record_id = await database.execute(query)

    query = select(user_request_booking_hostel_view).where(user_request_booking_hostel_view.c.user_id == user.user_id,
                                                           user_request_booking_hostel_view.c.university_id == university_id)

    result = await database.fetch_one(query)

    prepared_data = {
        "context": result,
        "service_id": user_request.service_id,
        "user_request_id": last_record_id
    }

    await create_user_document(**prepared_data)

    return {
        "status_id": STATUS_MAPPING.get("Розглядається"),
        "user_request_id": last_record_id
    }


@router.get("/{university_id}/user-request-booking-hostel/", response_model=UserRequestBookingHostelOut,
            tags=["Student dashboard"])
async def read_user_request_booking_hostel(university_id: int, user=Depends(get_current_user)):
    query = select(user_request_booking_hostel_view).where(user_request_booking_hostel_view.c.user_id == user.user_id,
                                                           user_request_booking_hostel_view.c.university_id == university_id)
    return await database.fetch_one(query)


@router.put("/{university_id}/user-request/{user_request_id}", response_model=CancelRequestOut,
            tags=["Student dashboard"])
async def cancel_request(university_id: int, user_request_id: int, cancel_request: CancelRequestIn, user=Depends(get_current_user)):
    CancelRequestIn(status_id=cancel_request.status_id)
    query = update(UserRequest).where(UserRequest.user_request_id == user_request_id).values(
        status_id=cancel_request.status_id)
    await database.execute(query)

    return {
        "user_request_id": user_request_id,
        "status_id": cancel_request.status_id
    }


@router.post("/{university_id}/user-request-review/{user_request_id}/", response_model=UserRequestReviewOut,
             tags=["Admin dashboard"])
async def create_user_request_review(university_id: int, user_request_id: int, user_request_review: UserRequestReviewIn,
                                     user=Depends(get_current_user)):
    query = insert(UserRequestReview).values(university_id=university_id,
                                             user_request_id=user_request_id,
                                             date_created=datetime.now(),
                                             reviewer=user.user_id,
                                             hostel_id=user_request_review.hostel_id,
                                             room_number=user_request_review.room_number,
                                             start_date_accommodation=user_request_review.start_date_accommodation.now(),
                                             end_date_accommodation=user_request_review.end_date_accommodation.now(),
                                             total_sum=user_request_review.total_sum,
                                             payment_deadline=user_request_review.payment_deadline.now(),
                                             remark=user_request_review.remark,
                                             date_review=datetime.now(),
                                             bed_place_id=user_request_review.bed_place_id)

    last_record_id = await database.execute(query)

    query = update(UserRequest).values(status_id=user_request_review.status_id).where(UserRequest.user_request_id == user_request_id)
    await database.execute(query)

    return {
        "status_id": user_request_review.status_id,
        "user_request_review_id": last_record_id
    }


@router.get("/{university_id}/hostel-accommodation/{user_request_id}", response_model=HostelAccomodationViewOut,
            tags=["Student dashboard"])
async def read_hostel_accommodation(university_id: int, user_request_id: int, user=Depends(get_current_user)):
    query = select(hostel_accommodation_view).where(hostel_accommodation_view.c.university_id == university_id,
                                                    hostel_accommodation_view.c.user_request_id == user_request_id)
    response = await database.fetch_one(query)

    response.documents = json.loads(response.documents)
    response.hostel_name = json.loads(response.hostel_name)
    response.hostel_address = json.loads(response.hostel_address)
    return response


@router.get("/{university_id}/user-request/{user_request_id}", response_model=UserRequestDetailsViewOut,
            tags=["Student dashboard"])
async def read_request_details(university_id: int, user_request_id: int, user=Depends(get_current_user)):
    query = select(user_request_details_view).where(user_request_details_view.c.university_id == university_id,
                                                    user_request_details_view.c.user_request_id == user_request_id)

    response = await database.fetch_one(query)

    response.documents = json.loads(response.documents)
    response.hostel_name = json.loads(response.hostel_name)
    return response