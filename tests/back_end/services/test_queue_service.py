from app.back_end.services.queue_service import QueueService
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


def test_next_track_in_normal_mode_returns_next_track():
    service = QueueService(track_ids=["t1", "t2", "t3"])

    response = service.next_track("t1")

    assert response.status is True
    assert response.message is SuccessMessage.QUEUE_TRACK_RESOLVED
    assert response.data == {"track_id": "t2"}


def test_previous_track_in_normal_mode_returns_previous_track():
    service = QueueService(track_ids=["t1", "t2", "t3"])

    response = service.previous_track("t2")

    assert response.status is True
    assert response.message is SuccessMessage.QUEUE_TRACK_RESOLVED
    assert response.data == {"track_id": "t1"}


def test_next_track_at_end_with_repeat_off_returns_none():
    service = QueueService(track_ids=["t1", "t2", "t3"])

    response = service.next_track("t3")

    assert response.status is True
    assert response.message is SuccessMessage.QUEUE_TRACK_RESOLVED
    assert response.data == {"track_id": None}


def test_next_track_at_end_with_repeat_all_wraps_to_start():
    service = QueueService(track_ids=["t1", "t2", "t3"])
    service.set_repeat_mode("repeat_all")

    response = service.next_track("t3")

    assert response.status is True
    assert response.data == {"track_id": "t1"}


def test_repeat_one_mode_returns_same_track_for_next_and_previous():
    service = QueueService(track_ids=["t1", "t2", "t3"])
    service.set_repeat_mode("repeat_one")

    next_response = service.next_track("t2")
    previous_response = service.previous_track("t2")

    assert next_response.status is True
    assert next_response.data == {"track_id": "t2"}
    assert previous_response.status is True
    assert previous_response.data == {"track_id": "t2"}


def test_shuffle_mode_changes_order_deterministically_with_seed():
    service = QueueService(track_ids=["t1", "t2", "t3"])
    service.set_shuffle(True, seed=7)

    response = service.previous_track("t1")

    assert response.status is True
    assert response.data == {"track_id": "t3"}


def test_disabling_shuffle_restores_original_order():
    service = QueueService(track_ids=["t1", "t2", "t3"])
    service.set_shuffle(True, seed=7)
    service.set_shuffle(False)

    response = service.previous_track("t1")

    assert response.status is True
    assert response.data == {"track_id": None}


def test_invalid_repeat_mode_returns_error():
    service = QueueService(track_ids=["t1", "t2", "t3"])

    response = service.set_repeat_mode("invalid_mode")

    assert response.status is False
    assert response.message is ErrorMessage.INVALID_REPEAT_MODE
    assert response.data is None


def test_unknown_track_returns_error():
    service = QueueService(track_ids=["t1", "t2", "t3"])

    response = service.next_track("missing")

    assert response.status is False
    assert response.message is ErrorMessage.TRACK_NOT_FOUND_IN_QUEUE
    assert response.data is None
