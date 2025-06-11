"""
Celery configuration for HF DABBY system
Advanced task queue management with Redis backend
"""

import os
from celery import Celery
from datetime import timedelta

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery instance
celery_app = Celery(
    'hf_dabby',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['celery_tasks']
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        'celery_tasks.analyze_file': {'queue': 'analysis'},
        'celery_tasks.generate_audit_report': {'queue': 'reports'},
        'celery_tasks.calculate_tax': {'queue': 'tax'},
        'celery_tasks.consultation': {'queue': 'consultation'},
        'celery_tasks.periodic_audit_summary': {'queue': 'periodic'},
        'celery_tasks.periodic_tax_check': {'queue': 'periodic'},
        'celery_tasks.periodic_consultant_report': {'queue': 'periodic'},
    },
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_eager_result=True,
    
    # Worker configuration
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # Result backend
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        'master_name': 'sentinel',
        'retry_on_timeout': True,
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'daily-audit-summary': {
            'task': 'celery_tasks.periodic_audit_summary',
            'schedule': timedelta(hours=24),
            'options': {'queue': 'periodic'}
        },
        'weekly-tax-check': {
            'task': 'celery_tasks.periodic_tax_check',
            'schedule': timedelta(days=7),
            'options': {'queue': 'periodic'}
        },
        'monthly-consultant-report': {
            'task': 'celery_tasks.periodic_consultant_report',
            'schedule': timedelta(days=30),
            'options': {'queue': 'periodic'}
        },
        'cleanup-old-sessions': {
            'task': 'celery_tasks.cleanup_old_sessions',
            'schedule': timedelta(hours=6),
            'options': {'queue': 'maintenance'}
        },
    },
)

# Queue configuration
CELERY_QUEUES = {
    'analysis': {
        'routing_key': 'analysis',
        'exchange': 'analysis',
        'exchange_type': 'direct',
    },
    'reports': {
        'routing_key': 'reports',
        'exchange': 'reports',
        'exchange_type': 'direct',
    },
    'tax': {
        'routing_key': 'tax',
        'exchange': 'tax',
        'exchange_type': 'direct',
    },
    'consultation': {
        'routing_key': 'consultation',
        'exchange': 'consultation',
        'exchange_type': 'direct',
    },
    'periodic': {
        'routing_key': 'periodic',
        'exchange': 'periodic',
        'exchange_type': 'direct',
    },
    'maintenance': {
        'routing_key': 'maintenance',
        'exchange': 'maintenance',
        'exchange_type': 'direct',
    },
}

if __name__ == '__main__':
    celery_app.start()
