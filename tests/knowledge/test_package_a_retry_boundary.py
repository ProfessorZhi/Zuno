import pytest

from zuno.knowledge.ingestion import PackageAProductionIngestionRuntime


def _runtime(*, max_attempts: int) -> PackageAProductionIngestionRuntime:
    runtime = object.__new__(PackageAProductionIngestionRuntime)
    runtime.max_attempts = max_attempts
    return runtime


def test_retryable_failure_retries_until_max_attempts_including_first_attempt() -> None:
    runtime = _runtime(max_attempts=2)

    assert runtime._failure_terminal_status(
        retryable=True,
        prior_attempt_count=0,
    ) == "failed"
    assert runtime._failure_terminal_status(
        retryable=True,
        prior_attempt_count=1,
    ) == "dead_letter"


def test_non_retryable_failure_dead_letters_on_first_attempt() -> None:
    runtime = _runtime(max_attempts=3)

    assert runtime._failure_terminal_status(
        retryable=False,
        prior_attempt_count=0,
    ) == "dead_letter"


def test_retry_boundary_rejects_negative_prior_attempt_count() -> None:
    runtime = _runtime(max_attempts=2)

    with pytest.raises(ValueError, match="prior_attempt_count"):
        runtime._failure_terminal_status(
            retryable=True,
            prior_attempt_count=-1,
        )
