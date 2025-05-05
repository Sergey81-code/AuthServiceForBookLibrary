import asyncio
from uuid import uuid4

import pytest

from tests.conftest import create_test_auth_headers_for_user
from tests.conftest import USER_URL
from tests.conftest import CHANGE_COUNT_OF_BORROWED_BOOKS
from utils.roles import PortalRole


async def test_change_count_of_borrowed_user_books(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "count_of_borrowed_books": 8,
        "password": "Abcd12!@",
        "is_active": True
    }

    admin_data = {
        "user_id": uuid4(),
        "name": "Nikolaiv",
        "surname": "Sviridovv",
        "email": "lol1@kek.com",
        "password": "Abcd12!@",
        "is_active": True,
        "roles": [PortalRole.ROLE_PORTAL_ADMIN]
    }

    count_of_borrowed_user_books_updated = {
        "count_of_borrowed_books" : 9
    }

    await create_user_in_database(user_data)
    await create_user_in_database(admin_data)

    resp = client.post(
        f"{USER_URL}{CHANGE_COUNT_OF_BORROWED_BOOKS}?user_id={user_data['user_id']}",
        headers=await create_test_auth_headers_for_user(admin_data["email"]),
        json=count_of_borrowed_user_books_updated,
    )

    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data == str(user_data["user_id"])

    users_from_db = await get_user_from_database(user_data["user_id"])
    assert len(users_from_db) == 1

    user_from_db = dict(users_from_db[0])
    assert user_from_db["count_of_borrowed_books"] == count_of_borrowed_user_books_updated["count_of_borrowed_books"]


@pytest.mark.parametrize(
    "user_id, user_changed_count_of_borrowed_books, expected_status_code, expected_detail",
    [
        (
            "",
            {},
            422,
            {
                "detail": [
                    {
                        "type": "uuid_parsing",
                        "loc": [
                            "query",
                            "user_id"
                        ],
                        "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 0",
                        "input": "",
                        "ctx": {
                            "error": "invalid length: expected length 32 for simple format, found 0"
                        }
                    },
                    {
                        "type": "missing",
                        "loc": [
                            "body",
                            "count_of_borrowed_books"
                        ],
                        "msg": "Field required",
                        "input": {}
                    }
                ]
            },
        ),
        (
            "123",
            {},
            422,
            {
                "detail": [
                    {
                        "type": "uuid_parsing",
                        "loc": [
                            "query",
                            "user_id"
                        ],
                        "msg": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 3",
                        "input": "123",
                        "ctx": {
                            "error": "invalid length: expected length 32 for simple format, found 3"
                        }
                    },
                    {
                        "type": "missing",
                        "loc": [
                            "body",
                            "count_of_borrowed_books"
                        ],
                        "msg": "Field required",
                        "input": {}
                    }
                ]
            },
        ),
        (
            "06815f2f-0944-78b6-8000-8cb811cc4533",
            {},
            422,
            {
                "detail": [
                    {
                        "type": "missing",
                        "loc": [
                            "body",
                            "count_of_borrowed_books"
                        ],
                        "msg": "Field required",
                        "input": {}
                    }
                ]
            },
        ),
        (
            "06815f2f-0944-78b6-8000-8cb811cc4533",
            {"count_of_borrowed_books": -4},
            400,
            {
                "detail": "Count of borrowed books can be from 0 to 10."
            },
        ),
        (
            "06815f2f-0944-78b6-8000-8cb811cc4533",
            {"count_of_borrowed_books": 85},
            400,
            {
                "detail": "Count of borrowed books can be from 0 to 10."
            },
        ),
        (
            "06815f2f-0944-78b6-8000-8cb811cc4533",
            {"count_of_borrowed_books": "eret"},
            422,
            {
                "detail": [
                    {
                        "type": "int_parsing",
                        "loc": [
                            "body",
                            "count_of_borrowed_books"
                        ],
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                        "input": "eret"
                    }
                ]
            },
        ),
        (
            "06815f2f-0944-78b6-8000-8cb811cc4533",
            {"count_of_borrowed_books": 8},
            404,
            {
                "detail": "User with id 06815f2f-0944-78b6-8000-8cb811cc4533 not found."
            },
        ),
    ],
)
async def test_change_count_of_borrowed_user_books_validation_error(
    client,
    create_user_in_database,
    user_id,
    user_changed_count_of_borrowed_books,
    expected_status_code,
    expected_detail,
):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "password": "Abcd12!@",
        "is_active": True,
    }

    admin_data = {
        "user_id": uuid4(),
        "name": "Nikolaiv",
        "surname": "Sviridovv",
        "email": "lol1@kek.com",
        "password": "Abcd12!@",
        "is_active": True,
        "roles": [PortalRole.ROLE_PORTAL_ADMIN]
    }

    await create_user_in_database(user_data)
    await create_user_in_database(admin_data)

    resp = client.post(
        f"{USER_URL}{CHANGE_COUNT_OF_BORROWED_BOOKS}?user_id={user_id}",
        headers=await create_test_auth_headers_for_user(admin_data["email"]),
        json=user_changed_count_of_borrowed_books,
    )

    assert resp.status_code == expected_status_code
    resp_data = resp.json()
    assert resp_data == expected_detail


async def test_change_count_of_borrowed_user_books_bad_cred(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "count_of_borrowed_books": 8,
        "password": "Abcd12!@",
        "is_active": True
    }

    admin_data = {
        "user_id": uuid4(),
        "name": "Nikolaiv",
        "surname": "Sviridovv",
        "email": "lol1@kek.com",
        "password": "Abcd12!@",
        "is_active": True,
        "roles": [PortalRole.ROLE_PORTAL_ADMIN]
    }

    count_of_borrowed_user_books_updated = {
        "count_of_borrowed_books" : 9
    }

    await create_user_in_database(user_data)
    await create_user_in_database(admin_data)

    resp = client.post(
        f"{USER_URL}{CHANGE_COUNT_OF_BORROWED_BOOKS}?user_id={user_data['user_id']}",
        headers=await create_test_auth_headers_for_user(admin_data["email"] + "a"),
        json=count_of_borrowed_user_books_updated,
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}



async def test_change_count_of_borrowed_user_books_unauth(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "count_of_borrowed_books": 8,
        "password": "Abcd12!@",
        "is_active": True
    }

    admin_data = {
        "user_id": uuid4(),
        "name": "Nikolaiv",
        "surname": "Sviridovv",
        "email": "lol1@kek.com",
        "password": "Abcd12!@",
        "is_active": True,
        "roles": [PortalRole.ROLE_PORTAL_ADMIN]
    }

    count_of_borrowed_user_books_updated = {
        "count_of_borrowed_books" : 9
    }

    await create_user_in_database(user_data)
    await create_user_in_database(admin_data)

    bad_auth_headers = await create_test_auth_headers_for_user(admin_data["email"])
    bad_auth_headers["Authorization"] += "a"

    resp = client.post(
        f"{USER_URL}{CHANGE_COUNT_OF_BORROWED_BOOKS}?user_id={user_data['user_id']}",
        headers=bad_auth_headers,
        json=count_of_borrowed_user_books_updated,
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}



async def test_change_count_of_borrowed_user_books_no_jwt(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "count_of_borrowed_books": 8,
        "password": "Abcd12!@",
        "is_active": True
    }

    count_of_borrowed_user_books_updated = {
        "count_of_borrowed_books" : 9
    }

    await create_user_in_database(user_data)

    resp = client.post(
        f"{USER_URL}{CHANGE_COUNT_OF_BORROWED_BOOKS}?user_id={user_data['user_id']}",
        json=count_of_borrowed_user_books_updated,
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(
    "user_role_list",
    [
        [PortalRole.ROLE_PORTAL_USER, PortalRole.ROLE_PORTAL_ADMIN],
        [PortalRole.ROLE_PORTAL_USER, PortalRole.ROLE_PORTAL_SUPERADMIN],
        [PortalRole.ROLE_PORTAL_ADMIN, PortalRole.ROLE_PORTAL_SUPERADMIN],
    ],
)
async def test_change_count_of_borrowed_user_books_by_privilage_roles(
    client, create_user_in_database, get_user_from_database, user_role_list
):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "count_of_borrowed_books": 8,
        "password": "Abcd12!@",
        "is_active": True,
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }

    admin_data = {
        "user_id": uuid4(),
        "name": "Nikolaiv",
        "surname": "Sviridovv",
        "email": "lol1@kek.com",
        "password": "Abcd12!@",
        "is_active": True,
        "roles": user_role_list,
    }

    count_of_borrowed_user_books_updated = {
        "count_of_borrowed_books" : 9
    }

    await create_user_in_database(user_data)
    await create_user_in_database(admin_data)

    resp = client.post(
        f"{USER_URL}{CHANGE_COUNT_OF_BORROWED_BOOKS}?user_id={user_data['user_id']}",
        headers=await create_test_auth_headers_for_user(admin_data["email"]),
        json=count_of_borrowed_user_books_updated,
    )

    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data == str(user_data["user_id"])

    users_from_db = await get_user_from_database(user_data["user_id"])
    assert len(users_from_db) == 1

    user_from_db = dict(users_from_db[0])
    assert user_from_db["count_of_borrowed_books"] == count_of_borrowed_user_books_updated["count_of_borrowed_books"]


@pytest.mark.parametrize(
    "user_data_for_changing, user_who_change",
    [
        (
            {
                "user_id": uuid4(),
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "is_active": True,
                "password": "SampleHashedPass",
                "count_of_borrowed_books": 7,
                "roles": [PortalRole.ROLE_PORTAL_USER],
            },
            {
                "user_id": uuid4(),
                "name": "Admin",
                "surname": "Adminov",
                "email": "admin@kek.com",
                "is_active": True,
                "password": "SampleHashedPass",
                "roles": [PortalRole.ROLE_PORTAL_USER],
            },
        ),
        (
            {
                "user_id": uuid4(),
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "is_active": True,
                "count_of_borrowed_books": 7,
                "password": "SampleHashedPass",
                "roles": [
                    PortalRole.ROLE_PORTAL_USER,
                    PortalRole.ROLE_PORTAL_SUPERADMIN,
                ],
            },
            {
                "user_id": uuid4(),
                "name": "Admin",
                "surname": "Adminov",
                "email": "admin@kek.com",
                "is_active": True,
                "count_of_borrowed_books": 7,
                "password": "SampleHashedPass",
                "roles": [
                    PortalRole.ROLE_PORTAL_USER,
                    PortalRole.ROLE_PORTAL_ADMIN,
                ],
            },
        ),
        (
            {
                "user_id": uuid4(),
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "is_active": True,
                "count_of_borrowed_books": 7,
                "password": "SampleHashedPass",
                "roles": [
                    PortalRole.ROLE_PORTAL_USER,
                    PortalRole.ROLE_PORTAL_ADMIN,
                ],
            },
            {
                "user_id": uuid4(),
                "name": "Admin",
                "surname": "Adminov",
                "email": "admin@kek.com",
                "is_active": True,
                "password": "SampleHashedPass",
                "roles": [
                    PortalRole.ROLE_PORTAL_USER,
                    PortalRole.ROLE_PORTAL_ADMIN,
                ],
            },
        ),
    ],
)
async def test_change_count_of_borrowed_user_books_privilage_error(
    client,
    create_user_in_database,
    user_data_for_changing,
    user_who_change,
):
    updated_count_of_borrowed_books = {
        "count_of_borrowed_books": 6
    }
    await create_user_in_database(user_data_for_changing)
    await create_user_in_database(user_who_change)

    reps = client.post(
        f"{USER_URL}{CHANGE_COUNT_OF_BORROWED_BOOKS}?user_id={user_data_for_changing['user_id']}",
        json=updated_count_of_borrowed_books,
        headers=await create_test_auth_headers_for_user(user_who_change["email"]),
    )
    assert reps.status_code == 403
