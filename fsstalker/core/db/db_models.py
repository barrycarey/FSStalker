from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey, Index, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

"""
class WatchToNotification(Base):
    __tablename__ = 'association'
    left_id = Column(Integer, ForeignKey('left.id'), primary_key=True)
    right_id = Column(Integer, ForeignKey('right.id'), primary_key=True)

    extra_data = Column(String(50))

    left = relationship('Left', backref=backref('right_association'))
    right = relationship('Right', backref=backref('left_association'))
"""
association_table = Table('watch_to_notification', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('watch_id', Integer, ForeignKey('watch.id'), nullable=False),
    Column('notification_service_id', Integer, ForeignKey('notification_service.id'), nullable=False)
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
    sent_notifications = relationship('SentNotification', back_populates='watch', cascade='all, delete-orphan')
    notification_services = relationship(
        'NotificationService',
        secondary=association_table,
        back_populates='watches'
    )



class NotificationService(Base):
    __tablename__ = 'notification_service'
    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False, unique=True)
    owner_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(200), nullable=False)
    owner = relationship('User', back_populates='notification_services')
    watches = relationship(
        "Watch",
        secondary=association_table,
        back_populates='notification_services'
    )


class SentNotification(Base):
    __tablename__ = 'sent_notification'
    id = Column(Integer, primary_key=True)
    sent_at = Column(DateTime, default=func.utc_timestamp())
    submission_created_at = Column(DateTime, nullable=False)
    triggered_post = Column(String(6), nullable=False)
    triggered_word = Column(String(100), nullable=False)
    expected_delay = Column(Integer, nullable=False)
    actual_delay = Column(Integer, nullable=False)
    watch_id = Column(Integer, ForeignKey('watch.id'))
    owner_id = Column(Integer, ForeignKey('user.id'))
    watch = relationship('Watch', back_populates='sent_notifications')
    owner = relationship('User', back_populates='sent_notifications')

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
    patreon_tier_id = Column(Integer, ForeignKey('patreon_tiers.id'), default=1)
    is_mod = Column(Boolean, default=False)
    is_exempt = Column(Boolean, default=False)
    patreon_id = Column(String(30))
    watches = relationship('Watch', back_populates='owner')
    notification_services = relationship("NotificationService", back_populates='owner')
    patreon_tier = relationship('PatreonTier')
    user_notifications = relationship('UserNotification', back_populates='owner')
    sent_notifications = relationship('SentNotification', back_populates='owner')

    def __repr__(self):
        return f'User {self.username}'

class PatreonTier(Base):
    __tablename__ = 'patreon_tiers'
    id = Column(Integer, primary_key=True)
    tier_id = Column(Integer)
    name = Column(String(40), nullable=False)
    max_watches = Column(Integer, nullable=False, default=1)
    max_notification_services = Column(Integer, nullable=False, default=1)
    notify_delay = Column(Integer, nullable=False, default=1800)

class UserNotification(Base):
    __tablename__ = 'user_notification'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.utc_timestamp())
    read = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('user.id'))
    message = Column(String(300), nullable=False)
    type = Column(String(20), nullable=False)
    owner = relationship('User', back_populates='user_notifications')