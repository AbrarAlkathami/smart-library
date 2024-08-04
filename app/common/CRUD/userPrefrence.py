
from sqlalchemy.orm import Session 
from schemas.user import UserPreferenceSchema
from common.database.models import UserPreference


def create_user_preference(db: Session, preference: UserPreferenceSchema, username: str):
    db_preference = UserPreference(
        username=username,
        preference_type=preference.preference_type,
        preference_value=preference.preference_value
    )
    db.add(db_preference)
    db.commit()
    db.refresh(db_preference)
    return db_preference

def get_user_preferences(db: Session, username: str):
    return db.query(UserPreference).filter(UserPreference.username == username).all()