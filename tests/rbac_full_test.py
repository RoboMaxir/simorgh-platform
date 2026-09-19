def test_database():

    SessionLocal = None

    try:
        from app.db.session import SessionLocal

    except ImportError:

        try:
            from app.db.database import SessionLocal

        except ImportError:

            try:
                from app.db import SessionLocal

            except ImportError:
                raise Exception(
                    "Database SessionLocal location not found"
                )


    db = SessionLocal()

    try:

        from sqlalchemy import text

        result = db.execute(
            text("SELECT 1")
        )

        return result is not None

    finally:
        db.close()
