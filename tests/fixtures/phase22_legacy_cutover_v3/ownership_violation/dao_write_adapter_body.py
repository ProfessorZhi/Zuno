"""Public adapter ownership violation fixture — direct DAO write.

The fixture is dropped into one of the public adapter modules during
the test to trigger the ownership detector.
"""


def adapter_with_dao_write(session, entity):
    """A public adapter that bypasses the canonical runtime by writing
    directly to the database. This is an ownership violation."""
    session.add(entity)
    session.commit()
    return entity
