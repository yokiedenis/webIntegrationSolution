"""LLM Fallback Provider with circuit breaker pattern."""

import logging
import time
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """States for circuit breaker pattern."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, use fallback
    HALF_OPEN = "half_open"  # Testing if recovered


class LLMFallbackProvider:
    """Wraps LLM providers with fallback chain and circuit breaker."""

    def __init__(
        self,
        primary_provider: Optional[Any] = None,
        fallback_provider: Optional[Any] = None,
        failure_threshold: int = 3,
        recovery_timeout: int = 60,
    ):
        """
        Initialize fallback provider.

        Args:
            primary_provider: Primary LLM provider (e.g., litellm)
            fallback_provider: Fallback provider if primary fails
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before retrying after circuit opens
        """
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        # Circuit breaker state
        self.circuit_state = CircuitBreakerState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.total_failures = 0
        self.total_successes = 0

    def classify_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """Classify intent with fallback chain."""
        # Try primary provider
        if self.primary_provider and self._can_try_primary():
            try:
                result = self.primary_provider.classify_intent(message)
                self._record_success()
                return result
            except Exception as e:
                logger.warning(f"Primary provider failed: {e}")
                self._record_failure()

        # Try fallback provider
        if self.fallback_provider:
            try:
                result = self.fallback_provider.classify_intent(message)
                return result
            except Exception as e:
                logger.warning(f"Fallback provider failed: {e}")

        # Return None if all providers fail
        return None

    def generate_response(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate response with fallback chain."""
        # Try primary provider
        if self.primary_provider and self._can_try_primary():
            try:
                response = self.primary_provider.generate_response(message, context)
                self._record_success()
                return response
            except Exception as e:
                logger.warning(f"Primary response generation failed: {e}")
                self._record_failure()

        # Try fallback provider
        if self.fallback_provider:
            try:
                response = self.fallback_provider.generate_response(message, context)
                return response
            except Exception as e:
                logger.warning(f"Fallback response generation failed: {e}")

        return None

    def _can_try_primary(self) -> bool:
        """Determine if we should try primary provider (circuit breaker)."""
        if self.circuit_state == CircuitBreakerState.CLOSED:
            return True

        if self.circuit_state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if (
                self.last_failure_time
                and time.time() - self.last_failure_time > self.recovery_timeout
            ):
                # Try half-open state
                self.circuit_state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker: Entering HALF_OPEN state")
                return True
            return False

        # HALF_OPEN - allow one attempt
        return True

    def _record_success(self):
        """Record successful operation."""
        self.total_successes += 1
        self.consecutive_failures = 0

        if self.circuit_state == CircuitBreakerState.HALF_OPEN:
            self.circuit_state = CircuitBreakerState.CLOSED
            logger.info("Circuit breaker: Recovered to CLOSED state")

    def _record_failure(self):
        """Record failed operation."""
        self.total_failures += 1
        self.consecutive_failures += 1
        self.last_failure_time = time.time()

        if self.consecutive_failures >= self.failure_threshold:
            if self.circuit_state != CircuitBreakerState.OPEN:
                self.circuit_state = CircuitBreakerState.OPEN
                logger.error(
                    f"Circuit breaker: OPENED after {self.consecutive_failures} "
                    f"consecutive failures"
                )

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker health metrics."""
        total_attempts = self.total_successes + self.total_failures
        success_rate = (
            self.total_successes / total_attempts * 100 if total_attempts > 0 else 0
        )

        return {
            "circuit_state": self.circuit_state.value,
            "consecutive_failures": self.consecutive_failures,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "success_rate": success_rate,
            "last_failure_time": self.last_failure_time,
            "is_available": self.circuit_state != CircuitBreakerState.OPEN,
        }

    def reset(self):
        """Reset circuit breaker state."""
        self.circuit_state = CircuitBreakerState.CLOSED
        self.consecutive_failures = 0
        self.total_failures = 0
        self.total_successes = 0
        self.last_failure_time = None
        logger.info("Circuit breaker: Reset to initial state")
