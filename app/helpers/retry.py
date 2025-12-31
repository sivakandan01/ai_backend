import asyncio
import logging
from functools import wraps
from typing import Callable, TypeVar, Any
import httpx
from app.constants.validation import MAX_RETRY_ATTEMPTS

logger = logging.getLogger(__name__)

T = TypeVar('T')

def async_retry(
    max_attempts: int = MAX_RETRY_ATTEMPTS + 1,  # Total attempts (1 initial + MAX_RETRY_ATTEMPTS retries)
    retry_on: tuple = (httpx.TimeoutException, httpx.ConnectError),
    retry_on_status: tuple = (503, 504, 429),  # Service Unavailable, Gateway Timeout, Too Many Requests
    delay: float = 1.0,  # Initial delay in seconds
    backoff_multiplier: float = 2.0  # Exponential backoff multiplier
):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    result = await func(*args, **kwargs)
                    if attempt > 1:
                        logger.info(f"{func.__name__} succeeded on attempt {attempt}/{max_attempts}")
                    return result

                except httpx.HTTPStatusError as e:
                    last_exception = e
                    # Check if this status code should be retried
                    if e.response and e.response.status_code in retry_on_status:
                        if attempt < max_attempts:
                            logger.warning(
                                f"{func.__name__} got HTTP {e.response.status_code} on attempt {attempt}/{max_attempts}. "
                                f"Retrying in {current_delay}s..."
                            )
                            await asyncio.sleep(current_delay)
                            current_delay *= backoff_multiplier
                            continue
                    # If status code shouldn't be retried or max attempts reached, raise
                    raise

                except retry_on as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} failed with {type(e).__name__} on attempt {attempt}/{max_attempts}. "
                            f"Retrying in {current_delay}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_multiplier
                        continue
                    else:
                        # Max attempts reached, log and raise
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts with {type(e).__name__}"
                        )
                        raise

                except Exception as e:
                    # Don't retry on other exceptions
                    logger.error(f"{func.__name__} failed with non-retryable exception: {type(e).__name__}")
                    raise

            # This should not be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator
