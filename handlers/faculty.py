from models.faculty import faculty as faculty_table
from models.faculty_list_view import faculty_list_view
from schemas.faculty import FacultyOut, FacultyIn
from handlers.current_user import get_current_user
from db import database

from typing import List

from fastapi import Depends, APIRouter

from schemas.jsend import JSENDOutSchema

router = APIRouter()


@router.get("/{university_id}/faculties/", response_model=JSENDOutSchema[List[FacultyOut]],
            tags=["SuperAdmin dashboard"])  # TODO after input id of non-existent university it returns success
async def read_faculties(university_id: int, user=Depends(get_current_user)):
    query = faculty_list_view.select().where(faculty_list_view.c.university_id == university_id)
    return JSENDOutSchema[List[FacultyOut]](
        data=await database.fetch_all(query),
        message=f"Get faculties of the university with id {university_id}"
    )


@router.post("/{university_id}/faculties/", response_model=JSENDOutSchema[FacultyOut], tags=["SuperAdmin dashboard"])
async def create_faculty(university_id: int, faculty: FacultyIn, user=Depends(get_current_user)):
    query = faculty_table.insert().values(name=faculty.name, shortname=faculty.shortname,
                                          main_email=faculty.main_email,
                                          university_id=faculty.university_id)

    last_record_id = await database.execute(query)
    return JSENDOutSchema[FacultyOut](
        data={
            **faculty.dict(),
            "faculty_id": last_record_id
        },
        message=f"Successfully created faculty with id {last_record_id}"
    )
