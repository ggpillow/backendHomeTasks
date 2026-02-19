from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, field_validator


class IssueReason(str, Enum):
    NO_NETWORK = "нет доступа к сети"
    PHONE_NOT_WORKING = "не работает телефон"
    NO_EMAILS = "не приходят письма"


class AppealCreate(BaseModel):
    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        examples=["Иванов"],
    )
    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        examples=["Пётр"],
    )
    birth_date: date = Field(
        ...,
        examples=["1990-05-15"],
    )
    phone: str = Field(
        ...,
        examples=["+79991234567"],
    )
    email: EmailStr = Field(
        ...,
        examples=["ivanov@example.com"],
    )
    reasons: list[IssueReason] = Field(
        ...,
        min_length=1,
        examples=[["нет доступа к сети", "не приходят письма"]],
    )
    issue_discovered_at: datetime = Field(
        ...,
        examples=["2025-01-15T14:30:00"],
    )

    @field_validator("last_name", "first_name")
    @classmethod
    def validate_cyrillic_name(cls, value: str, info) -> str:
        if not value[0].isupper():
            raise ValueError(
                f"{info.field_name}: должно начинаться с заглавной буквы"
            )
        allowed = value.replace("-", "")
        for char in allowed:
            if not ("\u0400" <= char <= "\u04FF"):
                raise ValueError(
                    f"{info.field_name}: только кириллица, "
                    f"найден символ '{char}'"
                )
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        import re
        if not re.match(r"^\+7\d{10}$", value):
            raise ValueError(
                "Формат телефона: +7XXXXXXXXXX"
            )
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Дата рождения не может быть в будущем")
        if value.year < 1900:
            raise ValueError("Дата рождения не может быть ранее 1900 года")
        return value

    @field_validator("issue_discovered_at")
    @classmethod
    def validate_issue_time(cls, value: datetime) -> datetime:
        if value.replace(tzinfo=None) > datetime.now():
            raise ValueError("Дата обнаружения проблемы не может быть в будущем")
        return value

    @field_validator("reasons")
    @classmethod
    def validate_unique_reasons(cls, value: list[IssueReason]) -> list[IssueReason]:
        return list(dict.fromkeys(value))