import logging
import time
from functools import wraps
from jsonrpcserver import Success, Error as JsonRpcError
from oslash import Right, Left

logger = logging.getLogger("transfers")

def log_request_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        request = args[1] if len(args) > 1 else None
        request_ip = "Unknown"
        request_body = "No body"

        if request and hasattr(request, "META"):
            request_ip = request.META.get("REMOTE_ADDR", "Unknown")
            request_body = getattr(request, "body", "No body")
            if isinstance(request_body, bytes):
                request_body = request_body.decode("utf-8", errors="ignore")

        logger.info(f"[START] {func.__name__} | IP={request_ip} | Body={request_body}")

        try:
            response = func(*args, **kwargs)
            processing_time = round(time.time() - start_time, 3)

            if isinstance(response, Right):  # Success
                response_str = f"Success: {response._value}"
            elif isinstance(response, Left):  # JsonRpcError
                error = response._error
                response_str = f"Error: {getattr(error, 'message', str(error))} (Code: {getattr(error, 'code', 'Unknown')})"
            else:
                response_str = str(response)


            logger.info(
                f"[END] {func.__name__} | IP={request_ip} | Time={processing_time}s | Response={response_str}"
            )
            return response
        except Exception as e:
            processing_time = round(time.time() - start_time, 3)
            logger.error(
                f"[ERROR] {func.__name__} | IP={request_ip} | Time={processing_time}s | Error={str(e)}"
            )
            raise
    return wrapper
