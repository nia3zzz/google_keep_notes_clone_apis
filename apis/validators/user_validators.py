from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Any


# creating a validator class model using the basemodel and providing the neccessary properties required for the validation, documentation link: https://docs.pydantic.dev/latest/#pydantic-examples
class CreateUserValidator(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field()
    profile_picture: Any
    password: str = Field(min_length=6)

    @field_validator("profile_picture")
    def validate_profile_picture(cls, file):
        # image type validation
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise ValueError("Only JPEG and PNG images are allowed.")

        # file size check of max 5mb
        if file.size > 5 * 1024 * 1024:
            raise ValueError("Image too large (max 5MB).")

        return file


# login class validator for the validation of the req bodies of email and a password for least 6 characters
class LoginValidator(BaseModel):
    email: EmailStr = Field()
    password: str = Field(min_length=6)
