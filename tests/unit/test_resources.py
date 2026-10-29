from leolm.audio import ResourceLease


def test_resource_lease_is_idempotent():
    calls = []
    lease = ResourceLease(object(), lambda: calls.append(True))
    lease.close()
    lease.close()
    assert len(calls) == 1
