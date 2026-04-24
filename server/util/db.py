from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class DB:
    _instance = None
    _lock = Lock()  # 线程安全锁

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DB, cls).__new__(cls)
                    cls._instance._init_engine(*args, **kwargs)
        return cls._instance

    def _init_engine(self, url: str, pool_size: int = 10, max_overflow: int = 20):
        """初始化数据库引擎，带有连接池和错误处理"""
        try:
            self.engine = create_engine(
                url,
                echo=True,
                future=True,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,  # 检测失效连接
                pool_recycle=3600,  # 1小时回收连接
                connect_args={
                    'connect_timeout': 10,
                    'charset': 'utf8mb4',
                }
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_session(self) -> Session:
        """
        获取一个新的数据库 session
        返回 Session 对象，使用完需要手动 close()
        """
        return self.SessionLocal()


# 从配置加载数据库 URL
from config.settings import get_settings
_settings = get_settings()
DATABASE_URL = _settings.database.url

# 延迟初始化单例实例
_db_singleton = None


def get_db_singleton():
    """获取 DB 单例实例，首次调用时初始化"""
    global _db_singleton
    if _db_singleton is None:
        _db_singleton = DB(
            DATABASE_URL,
            pool_size=_settings.database.pool_size,
            max_overflow=_settings.database.max_overflow
        )
    return _db_singleton

