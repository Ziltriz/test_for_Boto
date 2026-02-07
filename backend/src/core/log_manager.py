import logging
from logging.handlers import RotatingFileHandler
import gzip
from typing import Dict, Any
from pathlib import Path
from datetime import datetime, timedelta


class LogManager:
    _loggers = {}
    LOG_BASE_DIR = Path(__file__).resolve().parent.parent.parent / "logs"

    @staticmethod
    def _get_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
        """Создает или возвращает существующий логгер с заданным именем"""
        if name in LogManager._loggers:
            return LogManager._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        LogManager._loggers[name] = logger
        return logger

    @staticmethod
    def _add_file_handler(logger: logging.Logger, logfile_name: str, level: int):
        """Добавляет файловый обработчик к логгеру"""
        log_dir = LogManager.LOG_BASE_DIR / "backend"
        log_dir.mkdir(parents=True, exist_ok=True)

        filename = log_dir / f"{logfile_name}.log"

        handler = RotatingFileHandler(
            filename,
            maxBytes=100 * 1024 * 1024,   
            backupCount=5,
            encoding="utf-8"
        )
        handler.setLevel(level)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(module)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        # Избегаем дублирования обработчиков
        if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
            logger.addHandler(handler)

    @staticmethod
    def setup_loggers():
        """Настройка всех логгеров приложения"""

        # Логгеры для базы данных
        db_info_logger = LogManager._get_logger("database")
        db_error_logger = LogManager._get_logger("database_errors", logging.ERROR)

        LogManager._add_file_handler(db_info_logger, "database_info", logging.INFO)
        LogManager._add_file_handler(db_error_logger, "database_errors", logging.ERROR)

        # Логгеры для сетевых операций
        network_info_logger = LogManager._get_logger("network")
        network_error_logger = LogManager._get_logger("network_errors", logging.ERROR)

        LogManager._add_file_handler(network_info_logger, "network_info", logging.INFO)
        LogManager._add_file_handler(network_error_logger, "network_errors", logging.ERROR)

    @staticmethod
    async def log_database_info(message: str, data: Dict = None):
        """
        Логирование информационных сообщений
        базы данных
        """
        logger = logging.getLogger("database")
        logger.info(f"DB_INFO|{message}|" f" DATA: {data}")
    
    @staticmethod
    def sync_log_database_info(message: str, data: Dict = None):
        """
        Логирование информационных сообщений
        базы данных
        """
        logger = logging.getLogger("database")
        logger.info(f"DB_INFO|{message}|" f" DATA: {data}")

    @staticmethod
    async def log_database_error(error: str, query: str = None, params: Dict = None):
        """
        Логирование ошибок базы данных
        """
        logger = logging.getLogger("database_errors")
        logger.error(f"DB_ERROR|{error}|" f" QUERY: {query}|" f" PARAMS: {params}")
    
    @staticmethod
    def sync_log_database_error(error: str, query: str = None, params: Dict = None):
        """
        Логирование ошибок базы данных
        """
        logger = logging.getLogger("database_errors")
        logger.error(f"DB_ERROR|{error}|" f" QUERY: {query}|" f" PARAMS: {params}")

    @staticmethod
    async def log_network_info(endpoint: str, message: str, data: Dict = None):
        """Логирование сетевых операций"""
        logger = logging.getLogger("network")
        logger.info(f"NETWORK_INFO|{endpoint}|" f" MESSAGE: {message}|" f" DATA: {data}")

    @staticmethod
    async def log_network_error(endpoint: str, error: str, response: Dict = None):
        """Логирование сетевых ошибок"""

        logger = logging.getLogger("network_errors")
        logger.error(f"NETWORK_ERROR|{endpoint}|" f" ERROR: {error}|" f" RESPONSE: {response}")
    
    @staticmethod
    def sync_log_network_info(endpoint: str, message: str, data: Dict = None):
        """Логирование сетевых операций"""
        logger = logging.getLogger("network")
        logger.info(f"NETWORK_INFO|{endpoint}|" f" MESSAGE: {message}|" f" DATA: {data}")

    @staticmethod
    def sync_log_network_error(endpoint: str, error: str, response: Dict = None):
        """Логирование сетевых ошибок"""

        logger = logging.getLogger("network_errors")
        logger.error(f"NETWORK_ERROR|{endpoint}|" f" ERROR: {error}|" f" RESPONSE: {response}")

    @staticmethod
    def compress_old_logs(logfile: Path):
        """
        Сжатие старых логов
        """
        try:
            # Сжимаем файл
            archive_dir = Path("/src/logs/oldzip")

            compressed_file = archive_dir / f"{logfile.stem}_{datetime.now().strftime('%Y%m%d')}.gz"
            with open(logfile, "rb") as f_in:
                with gzip.open(compressed_file, "wb") as f_out:
                    f_out.writelines(f_in)

            with open(logfile, "w") as f_clear:
                f_clear.write("")

            print(f"Compressed and cleared log file: {logfile}")
        except Exception as e:
            print(f"Error compressing log file {logfile}: {e}")

    @staticmethod
    def check_logs():
        """
        Сжатие старых логов
        """
        log_dir = Path("/src/logs/backend")
        if not log_dir.exists():
            print("Log directory does not exist.")
            return

        one_week_ago = datetime.now() - timedelta(days=7)

        for logfile in log_dir.glob("*.log"):
            try:
                # Получаем время последнего изменения файла
                file_stat = logfile.stat()
                file_mtime = datetime.fromtimestamp(file_stat.st_mtime)

                # Если файл старше недели, архивируем его
                if file_mtime < one_week_ago:
                    LogManager.compress_old_logs(logfile)
            except Exception as e:
                print(f"Error processing log file {logfile}: {e}")
