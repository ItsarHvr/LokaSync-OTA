import logging
import json
from typing import Any, Dict, Optional
from pathlib import Path
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform colored output
colorama.init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    def format(self, record):
        # Get the original formatted message
        log_message = super().format(record)
        
        # Add color based on log level
        color = self.COLORS.get(record.levelname, '')
        if color:
            # Color the entire message
            log_message = f"{color}{log_message}{Style.RESET_ALL}"
        
        return log_message

class Logger:
    """
    Custom logger for LokaSync Backend with colored output and file separation
    """
    
    def __init__(self):
        self.log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Create separate loggers for different components
        self.api_logger = self._create_logger("api", "api.log")
        self.database_logger = self._create_logger("database", "database.log")
        self.mqtt_logger = self._create_logger("mqtt", "mqtt.log")
        self.system_logger = self._create_logger("system", "system.log")
        self.gdrive_logger = self._create_logger("gdrive", "gdrive.log")
    
    def _create_logger(self, name: str, filename: str) -> logging.Logger:
        """Create a logger with both file and console handlers"""
        logger = logging.getLogger(f"lokasync.{name}")
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = ColoredFormatter(
            f'{Fore.BLUE}%(asctime)s{Style.RESET_ALL} | '
            f'{Fore.MAGENTA}%(name)s{Style.RESET_ALL} | '
            f'%(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_dir / filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _format_json_data(self, data: Any) -> str:
        """Format JSON data for pretty printing"""
        if isinstance(data, (dict, list)):
            return json.dumps(data, indent=2, ensure_ascii=False)
        return str(data)
    
    # API Logger Methods
    def api_info(self, message: str, data: Optional[Dict] = None):
        """Log API information"""
        if data:
            message += f"\n{self._format_json_data(data)}"
        self.api_logger.info(f"🌐 {message}")
    
    def api_error(self, message: str, error: Optional[Exception] = None):
        """Log API errors"""
        if error:
            message += f" | Error: {str(error)}"
        self.api_logger.error(f"❌ {message}")
    
    def api_warning(self, message: str):
        """Log API warnings"""
        self.api_logger.warning(f"⚠️ {message}")
    
    # Database Logger Methods
    def db_info(self, message: str, data: Optional[Dict] = None):
        """Log database information"""
        if data:
            message += f"\n{self._format_json_data(data)}"
        self.database_logger.info(f"🗄️ {message}")
    
    def db_error(self, message: str, error: Optional[Exception] = None):
        """Log database errors"""
        if error:
            message += f" | Error: {str(error)}"
        self.database_logger.error(f"❌ {message}")
    
    def db_warning(self, message: str):
        """Log database warnings"""
        self.database_logger.warning(f"⚠️ {message}")
    
    # MQTT Logger Methods
    def mqtt_info(self, message: str, data: Optional[Dict] = None):
        """Log MQTT information"""
        if data:
            message += f"\n{self._format_json_data(data)}"
        self.mqtt_logger.info(f"📡 {message}")
    
    def mqtt_error(self, message: str, error: Optional[Exception] = None):
        """Log MQTT errors"""
        if error:
            message += f" | Error: {str(error)}"
        self.mqtt_logger.error(f"❌ {message}")
    
    def mqtt_warning(self, message: str):
        """Log MQTT warnings"""
        self.mqtt_logger.warning(f"⚠️ {message}")
    
    def mqtt_debug(self, message: str, data: Optional[Dict] = None):
        """Log MQTT debug information"""
        if data:
            message += f"\n{self._format_json_data(data)}"
        self.mqtt_logger.debug(f"🔍 {message}")
    
    # System Logger Methods
    def system_info(self, message: str):
        """Log system information"""
        self.system_logger.info(f"🚀 {message}")
    
    def system_error(self, message: str, error: Optional[Exception] = None):
        """Log system errors"""
        if error:
            message += f" | Error: {str(error)}"
        self.system_logger.error(f"❌ {message}")
    
    def system_warning(self, message: str):
        """Log system warnings"""
        self.system_logger.warning(f"⚠️ {message}")
    
    # Google Drive Logger Methods
    def gdrive_info(self, message: str, data: Optional[Dict] = None):
        """Log Google Drive information"""
        if data:
            message += f"\n{self._format_json_data(data)}"
        self.gdrive_logger.info(f"☁️ {message}")
    
    def gdrive_error(self, message: str, error: Optional[Exception] = None):
        """Log Google Drive errors"""
        if error:
            message += f" | Error: {str(error)}"
        self.gdrive_logger.error(f"❌ {message}")
    
    def gdrive_warning(self, message: str):
        """Log Google Drive warnings"""
        self.gdrive_logger.warning(f"⚠️ {message}")
    
    def gdrive_debug(self, message: str, data: Optional[Dict] = None):
        """Log Google Drive debug information"""
        if data:
            message += f"\n{self._format_json_data(data)}"
        self.gdrive_logger.debug(f"🔍 {message}")

# Create global logger instance
logger = Logger()