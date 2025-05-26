from pydantic import EmailStr, ValidationError


def is_email(email: str) -> bool:
    try:
        EmailStr._validate(email)
    except ValidationError:
        return False
    return True
