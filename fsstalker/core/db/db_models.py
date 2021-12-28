from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey, Index, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

"""
class WatchToNotification(Base):
    __tablename__ = 'watch_to_notification'
    watch_id = Column(Integer, ForeignKey('watch.id'))
    notification_service_id = Column(Integer, ForeignKey('notification_service.id'))
"""
association_table = Table('watch_to_notification', Base.metadata,
    Column('watch_id', Integer, ForeignKey('watch.id')),
    Column('notification_service_id', Integer, ForeignKey('notification_service.id'))
)
class Watch(Base):
    __tablename__ = 'watch'
    __table_args__ = (
        Index('idx_subreddit', 'subreddit'),
    )
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('user.id'))
    subreddit = Column(String(21), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.utc_timestamp())
    include = Column(String(500), nullable=False)
    exclude = Column(String(500))
    name = Column(String(200), nullable=False)

    owner = relationship("User", back_populates='watches')
    sent_notifications = relationship("SentNotification", back_populates='watch')
    notification_services = relationship(
        "NotificationService",
        secondary=association_table,
        back_populates='watches'
    )


class NotificationService(Base):
    __tablename__ = 'notification_service'
    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False, unique=True)
    owner_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(200), nullable=False)
    owner = relationship("User", back_populates='notification_services')
    watches = relationship(
        "Watch",
        secondary=association_table,
        back_populates='notification_services'
    )


class SentNotification(Base):
    __tablename__ = 'sent_notification'
    id = Column(Integer, primary_key=True)
    sent_at = Column(DateTime, default=func.utc_timestamp())
    triggered_post = Column(String(6), nullable=False)
    triggered_word = Column(String(100), nullable=False)
    watch_id = Column(Integer, ForeignKey('watch.id'))
    watch = relationship("Watch", back_populates='sent_notifications')

class CheckedPost(Base):
    __tablename__ = 'checked_post'
    id = Column(Integer, primary_key=True)
    checked_at = Column(DateTime, default=func.utc_timestamp())
    post_id = Column(String(6), unique=True)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.utc_timestamp())
    is_premium = Column(Boolean, default=False)
    is_mod = Column(Boolean, default=False)
    watches = relationship("Watch", back_populates='owner')
    notification_services = relationship("NotificationService", back_populates='owner')