from datetime import datetime, timezone


def utcnow():
    # O banco guarda datetimes UTC sem tzinfo; mantém esse formato.
    return datetime.now(timezone.utc).replace(tzinfo=None)
