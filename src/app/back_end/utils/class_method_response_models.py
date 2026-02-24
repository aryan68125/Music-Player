from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict

from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage

T = TypeVar("T")


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SuccessResponse(BaseResponseModel, Generic[T]):
    status: Literal[True] = True
    message: SuccessMessage
    data: T | list[T]


class ErrorResponse(BaseResponseModel):
    status: Literal[False] = False
    message: ErrorMessage
    data: None = None


type MethodResponse[T] = SuccessResponse[T] | ErrorResponse
