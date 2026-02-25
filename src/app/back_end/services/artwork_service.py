from __future__ import annotations

from pathlib import Path

from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from mutagen.mp4 import MP4, MP4Cover

from app.back_end.utils.class_method_response_models import ErrorResponse, MethodResponse, SuccessResponse
from app.back_end.utils.error_messages import ErrorMessage
from app.back_end.utils.success_messages import SuccessMessage


class ArtworkService:
    _SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".m4a", ".mp4", ".flac"}

    def replace_artwork(self, track_path: str, image_path: str) -> MethodResponse[dict[str, str]]:
        track = Path(track_path)
        image = Path(image_path)

        if not track.exists():
            return ErrorResponse(message=ErrorMessage.TRACK_NOT_FOUND)
        if track.suffix.lower() not in self._SUPPORTED_AUDIO_EXTENSIONS:
            return ErrorResponse(message=ErrorMessage.ARTWORK_FORMAT_NOT_SUPPORTED)
        if not image.exists() or not image.is_file():
            return ErrorResponse(message=ErrorMessage.ARTWORK_IMAGE_NOT_FOUND)

        image_data = image.read_bytes()
        mime = self._detect_image_mime(image_data)
        if mime is None:
            return ErrorResponse(message=ErrorMessage.INVALID_ARTWORK_IMAGE)

        try:
            extension = track.suffix.lower()
            if extension == ".mp3":
                self._replace_mp3(track, image_data, mime)
            elif extension in {".m4a", ".mp4"}:
                self._replace_mp4(track, image_data, mime)
            elif extension == ".flac":
                self._replace_flac(track, image_data, mime)
            else:
                return ErrorResponse(message=ErrorMessage.ARTWORK_FORMAT_NOT_SUPPORTED)
        except Exception:
            return ErrorResponse(message=ErrorMessage.ARTWORK_UPDATE_FAILED)

        return SuccessResponse[dict[str, str]](
            message=SuccessMessage.ARTWORK_UPDATED,
            data={"track_path": str(track), "image_path": str(image)},
        )

    def remove_artwork(self, track_path: str) -> MethodResponse[dict[str, str]]:
        track = Path(track_path)

        if not track.exists():
            return ErrorResponse(message=ErrorMessage.TRACK_NOT_FOUND)
        if track.suffix.lower() not in self._SUPPORTED_AUDIO_EXTENSIONS:
            return ErrorResponse(message=ErrorMessage.ARTWORK_FORMAT_NOT_SUPPORTED)

        try:
            extension = track.suffix.lower()
            if extension == ".mp3":
                self._remove_mp3(track)
            elif extension in {".m4a", ".mp4"}:
                self._remove_mp4(track)
            elif extension == ".flac":
                self._remove_flac(track)
            else:
                return ErrorResponse(message=ErrorMessage.ARTWORK_FORMAT_NOT_SUPPORTED)
        except Exception:
            return ErrorResponse(message=ErrorMessage.ARTWORK_REMOVE_FAILED)

        return SuccessResponse[dict[str, str]](
            message=SuccessMessage.ARTWORK_REMOVED,
            data={"track_path": str(track)},
        )

    @staticmethod
    def _detect_image_mime(image_data: bytes) -> str | None:
        if image_data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if image_data.startswith(b"\xFF\xD8\xFF"):
            return "image/jpeg"
        return None

    @staticmethod
    def _replace_mp3(track: Path, image_data: bytes, mime: str) -> None:
        try:
            tags = ID3(track)
        except ID3NoHeaderError:
            tags = ID3()

        tags.delall("APIC")
        tags.add(
            APIC(
                encoding=3,
                mime=mime,
                type=3,
                desc="Cover",
                data=image_data,
            )
        )
        tags.save(track, v2_version=3)

    @staticmethod
    def _remove_mp3(track: Path) -> None:
        try:
            tags = ID3(track)
        except ID3NoHeaderError:
            return

        tags.delall("APIC")
        tags.save(track, v2_version=3)

    @staticmethod
    def _replace_mp4(track: Path, image_data: bytes, mime: str) -> None:
        audio = MP4(track)
        cover_format = MP4Cover.FORMAT_PNG if mime == "image/png" else MP4Cover.FORMAT_JPEG
        audio["covr"] = [MP4Cover(image_data, imageformat=cover_format)]
        audio.save()

    @staticmethod
    def _remove_mp4(track: Path) -> None:
        audio = MP4(track)
        if "covr" in audio:
            del audio["covr"]
            audio.save()

    @staticmethod
    def _replace_flac(track: Path, image_data: bytes, mime: str) -> None:
        audio = FLAC(track)
        picture = Picture()
        picture.type = 3
        picture.desc = "Cover"
        picture.mime = mime
        picture.data = image_data
        audio.clear_pictures()
        audio.add_picture(picture)
        audio.save()

    @staticmethod
    def _remove_flac(track: Path) -> None:
        audio = FLAC(track)
        audio.clear_pictures()
        audio.save()
