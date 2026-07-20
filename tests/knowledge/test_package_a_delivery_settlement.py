import asyncio

from zuno.knowledge.ingestion import PackageAProductionIngestionRuntime, PackageAWorkerReceipt


class _RecordingDelivery:
    message_id = "event-1"
    payload = {}
    headers = {}
    redelivered = False

    def __init__(self) -> None:
        self.acked = False
        self.rejected = False
        self.requeue: bool | None = None

    async def ack(self) -> None:
        self.acked = True

    async def nack(self, *, requeue: bool) -> None:
        raise AssertionError("Package A settlement should not nack terminal receipts")

    async def reject(self, *, requeue: bool = False) -> None:
        self.rejected = True
        self.requeue = requeue


def test_package_a_settlement_acks_success_after_domain_commit() -> None:
    delivery = _RecordingDelivery()
    receipt = PackageAWorkerReceipt(
        parse_job_id="job-1",
        parse_attempt_id="attempt-1",
        status="succeeded",
        acked_after_domain_commit=True,
    )

    asyncio.run(
        PackageAProductionIngestionRuntime._settle_delivery_after_domain_commit(
            delivery=delivery,
            worker_receipt=receipt,
        )
    )

    assert delivery.acked is True
    assert delivery.rejected is False


def test_package_a_settlement_rejects_dead_letter_after_domain_commit() -> None:
    delivery = _RecordingDelivery()
    receipt = PackageAWorkerReceipt(
        parse_job_id="job-1",
        parse_attempt_id="attempt-1",
        status="dead_letter",
        acked_after_domain_commit=False,
        dead_letter_id="dead-letter:attempt-1",
    )

    asyncio.run(
        PackageAProductionIngestionRuntime._settle_delivery_after_domain_commit(
            delivery=delivery,
            worker_receipt=receipt,
        )
    )

    assert delivery.acked is False
    assert delivery.rejected is True
    assert delivery.requeue is False
