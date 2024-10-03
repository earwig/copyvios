__all__ = ["APIQuery", "CheckQuery", "SettingsQuery"]

from typing import Any, Literal, Self

from flask import request
from pydantic import BaseModel, field_validator, model_validator
from werkzeug.datastructures import MultiDict


class BaseQuery(BaseModel):
    @classmethod
    def from_multidict(cls, args: MultiDict[str, str]) -> Self:
        query = {key: args.getlist(key)[-1] for key in args}
        return cls.model_validate(query)

    @classmethod
    def from_get_args(cls) -> Self:
        return cls.from_multidict(request.args)

    @classmethod
    def from_post_data(cls) -> Self:
        return cls.from_multidict(request.form)


class CheckQuery(BaseQuery):
    action: str | None = None
    lang: str | None = None
    project: str | None = None
    title: str | None = None
    oldid: str | None = None
    url: str | None = None
    use_engine: bool = True
    use_links: bool = True
    turnitin: bool = False
    nocache: bool = False
    noredirect: bool = False
    noskip: bool = False
    degree: int | None = None

    # Derived parameters
    orig_lang: str | None = None
    name: str | None = None

    @field_validator("project")
    @classmethod
    def validate_project(cls, project: Any) -> str | None:
        if not isinstance(project, str):
            return project
        return project.strip().lower()

    @field_validator("oldid")
    @classmethod
    def validate_oldid(cls, oldid: Any) -> str | None:
        if not isinstance(oldid, str):
            return oldid
        return oldid.strip().lstrip("0")

    @model_validator(mode="after")
    def validate_lang(self) -> Self:
        self.orig_lang = self.name = None
        if self.lang:
            self.lang = self.orig_lang = self.lang.strip().lower()
            if "::" in self.lang:
                self.lang, self.name = self.lang.split("::", 1)
        return self

    @property
    def submitted(self) -> bool:
        return bool(self.project and self.lang and (self.title or self.oldid))


class APIQuery(CheckQuery):
    version: int = 1
    detail: bool = False


class SettingsQuery(BaseQuery):
    action: Literal["set", "delete"] | None = None

    # With action=set:
    lang: str | None = None
    project: str | None = None
    background: Literal["list", "potd", "plain"] | None = None

    # With action=delete:
    cookie: str | None = None
    all: bool | None = None
