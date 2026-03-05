from uuid import UUID

from pydantic import BaseModel, EmailStr


class OrgCreateRequest(BaseModel):
    org_name: str


class OrgCreateResponse(BaseModel):
    org_id: UUID


class InviteRequest(BaseModel):
    email: EmailStr
    role: str = "member"
