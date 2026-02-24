import pytest
from pydantic import TypeAdapter, ValidationError

from app.back_end.utils.class_method_request_models import (
    PlaylistReorderRequest,
    TrackPathRequest,
)
from app.back_end.utils.class_method_response_models import (
    ErrorResponse,
    MethodResponse,
    SuccessResponse,
)
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


def test_success_response_has_expected_shape_with_single_data():
    response = SuccessResponse[dict](message=SuccessMessage.GENERAL_SUCCESS, data={"id": 1})
    assert response.status is True
    assert response.message is SuccessMessage.GENERAL_SUCCESS
    assert response.data == {"id": 1}


def test_success_response_has_expected_shape_with_list_data():
    response = SuccessResponse[dict](message=SuccessMessage.GENERAL_SUCCESS, data=[{"id": 1}])
    assert response.status is True
    assert response.data == [{"id": 1}]


def test_error_response_has_expected_shape():
    response = ErrorResponse(message=ErrorMessage.UNKNOWN_ERROR)
    assert response.status is False
    assert response.message is ErrorMessage.UNKNOWN_ERROR
    assert response.data is None


def test_track_path_request_rejects_non_string_path():
    with pytest.raises(ValidationError):
        TrackPathRequest(path=123)


def test_playlist_reorder_request_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        PlaylistReorderRequest(playlist_id="abc", ordered_track_ids=["1", "2"], extra_key=1)


def test_method_response_union_parses_success_payload():
    adapter = TypeAdapter(MethodResponse[dict])
    parsed = adapter.validate_python(
        {
            "status": True,
            "message": SuccessMessage.GENERAL_SUCCESS,
            "data": {"id": 42},
        }
    )
    assert isinstance(parsed, SuccessResponse)
