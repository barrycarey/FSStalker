from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Watch(Base):
    __tablename__ = 'watch'
    id = Column(Integer, primary_key=True)
    owner = Column(String(20), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.utc_timestamp())
    include = Column(String(500))
    exclude = Column(String(500))

    notification_services = relationship("NotificationService")
    sent_notifications = relationship("SentNotification", back_populates='watch')


class NotificationService(Base):
    __tablename__ = 'notification_service'
    id = Column(Integer, primary_key=True)
    owner = Column(String(20), nullable=False)
    url = Column(String(200), nullable=False)



class SentNotification(Base):
    __tablename__ = 'sent_notification'
    id = Column(Integer, primary_key=True)
    sent_at = Column(DateTime, default=func.utc_timestamp())
    triggered_post = Column(String(6))
    watch_id = Column(Integer, ForeignKey('watch.id'))
    watch = relationship("Watch", back_populates='sent_notifications')