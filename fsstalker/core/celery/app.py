from celery import Celery
from kombu.serialization import registry

registry.enable('pickle')
celery = Celery('tasks')
celery.config_from_object('fsstalker.core.celery.config')


if __name__ == '__main__':
    celery.start()