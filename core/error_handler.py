"""
Error Handler - Robust Error Management with Retry Logic
========================================================

Provides comprehensive error handling and retry mechanisms for the A2A system.
"""

import time
import logging
from typing import Callable, Any, Optional, Dict
from functools import wraps
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Raised when all retry attempts have been exhausted"""
    pass


class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self, 
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def calculate_backoff_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate exponential backoff delay with optional jitter"""
    delay = min(
        config.initial_delay * (config.exponential_base ** (attempt - 1)),
        config.max_delay
    )
    
    if config.jitter:
        # Add jitter to prevent thundering herd
        import random
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay


def retry_with_backoff(
    func: Optional[Callable] = None,
    *,
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        func: Function to retry
        config: Retry configuration
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Callback function called on each retry
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return f(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    # Log the error
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed for {f.__name__}: {str(e)}"
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt)
                    
                    # If this was the last attempt, raise
                    if attempt == config.max_attempts:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {f.__name__}"
                        )
                        raise RetryError(
                            f"Failed after {config.max_attempts} attempts: {str(last_exception)}"
                        ) from last_exception
                    
                    # Calculate and apply backoff delay
                    delay = calculate_backoff_delay(attempt, config)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
            
            # Should never reach here
            raise RetryError("Unexpected retry loop exit")
        
        return wrapper
    
    # Handle both @retry_with_backoff and @retry_with_backoff() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


class ErrorLogger:
    """Centralized error logging with detailed tracking"""
    
    def __init__(self, log_file: str = "logs/error.log"):
        self.log_file = log_file
        
        # Create file handler for error logs
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
                'Stack Trace:\n%(exc_info)s\n' + '='*80 + '\n'
            )
        )
        
        # Add handler to logger
        self.logger = logging.getLogger("ErrorLogger")
        self.logger.addHandler(file_handler)
    
    def log_error(
        self, 
        error: Exception, 
        context: Dict[str, Any] = None,
        user_message: str = None
    ):
        """
        Log error with full context and stack trace
        
        Args:
            error: The exception that occurred
            context: Additional context information
            user_message: User-friendly error message
        """
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'stack_trace': traceback.format_exc()
        }
        
        # Log to file
        self.logger.error(
            f"Error occurred: {error_info['error_type']} - {error_info['error_message']}",
            exc_info=True,
            extra={'context': error_info['context']}
        )
        
        # Return user-friendly message
        if user_message:
            return user_message
        else:
            return self._generate_user_message(error)
    
    def _generate_user_message(self, error: Exception) -> str:
        """Generate user-friendly error message"""
        error_messages = {
            TimeoutError: "リクエストがタイムアウトしました。しばらく待ってから再試行してください。",
            ConnectionError: "接続エラーが発生しました。ネットワーク接続を確認してください。",
            ValueError: "入力値にエラーがあります。入力内容を確認してください。",
            RetryError: "複数回の試行後も処理が失敗しました。システム管理者にお問い合わせください。"
        }
        
        for error_type, message in error_messages.items():
            if isinstance(error, error_type):
                return message
        
        return "予期しないエラーが発生しました。詳細はログを確認してください。"


# Global error logger instance
error_logger = ErrorLogger()


def handle_api_timeout(func: Callable) -> Callable:
    """Specific handler for API timeout scenarios"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Set custom timeout config for API calls
            api_config = RetryConfig(
                max_attempts=3,
                initial_delay=2.0,
                max_delay=30.0
            )
            
            # Apply retry logic
            @retry_with_backoff(
                config=api_config,
                exceptions=(TimeoutError, ConnectionError),
                on_retry=lambda e, attempt: logger.info(
                    f"API call retry {attempt} due to: {str(e)}"
                )
            )
            def api_call():
                return func(*args, **kwargs)
            
            return api_call()
            
        except RetryError as e:
            # Log and return user-friendly message
            return error_logger.log_error(
                e,
                context={'function': func.__name__, 'args': args, 'kwargs': kwargs},
                user_message="API呼び出しが失敗しました。しばらく待ってから再試行してください。"
            )
    
    return wrapper