import pytest
from fastapi import HTTPException

from app.routers.appointments import validate_status_transition


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        ("scheduled", "scheduled"),
        ("scheduled", "confirmed"),
        ("scheduled", "cancelled"),
        ("confirmed", "confirmed"),
        ("confirmed", "completed"),
        ("confirmed", "cancelled"),
        ("completed", "completed"),
        ("cancelled", "cancelled"),
    ],
)
def test_status_transition_allows_valid_changes(
    current_status, new_status
):
    validate_status_transition(current_status, new_status)


@pytest.mark.parametrize(
    ("current_status", "new_status"),
    [
        ("scheduled", "completed"),
        ("confirmed", "scheduled"),
        ("completed", "scheduled"),
        ("completed", "confirmed"),
        ("completed", "cancelled"),
        ("cancelled", "scheduled"),
        ("cancelled", "confirmed"),
        ("cancelled", "completed"),
    ],
)
def test_status_transition_rejects_invalid_changes(
    current_status, new_status
):
    with pytest.raises(HTTPException) as exc_info:
        validate_status_transition(current_status, new_status)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == (
        f"Não é possível alterar o status de "
        f"'{current_status}' para '{new_status}'."
    )
