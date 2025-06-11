"""
Task Scheduler for HF DABBY system
Manages task execution for Auditor, Tax, and Consultant agents
Supports both Celery with Redis and APScheduler for periodic execution
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from agent_factory import AgentFactory
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    """Task scheduler for managing agent tasks"""
    
    def __init__(self, use_redis=False):
        self.use_redis = use_redis
        self.scheduler = None
        self.tasks = {}  # In-memory task storage
        self.agent_factory = AgentFactory()
        
        # Initialize scheduler
        self._init_scheduler()
        
    def _init_scheduler(self):
        """Initialize the scheduler"""
        job_stores = {
            'default': MemoryJobStore()
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=job_stores,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Task scheduler started")
            
            # Schedule some default periodic tasks
            self._schedule_default_tasks()
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")
    
    def _schedule_default_tasks(self):
        """Schedule default periodic tasks"""
        # Daily audit summary task
        self.scheduler.add_job(
            func=self._daily_audit_summary,
            trigger=CronTrigger(hour=9, minute=0),  # 9 AM UTC daily
            id='daily_audit_summary',
            name='Daily Audit Summary',
            replace_existing=True
        )
        
        # Weekly tax compliance check
        self.scheduler.add_job(
            func=self._weekly_tax_check,
            trigger=CronTrigger(day_of_week=1, hour=10, minute=0),  # Monday 10 AM
            id='weekly_tax_check',
            name='Weekly Tax Compliance Check',
            replace_existing=True
        )
        
        # Monthly consultant report
        self.scheduler.add_job(
            func=self._monthly_consultant_report,
            trigger=CronTrigger(day=1, hour=11, minute=0),  # 1st of month 11 AM
            id='monthly_consultant_report',
            name='Monthly Consultant Report',
            replace_existing=True
        )
        
        logger.info("Default periodic tasks scheduled")
    
    def schedule_task(
        self,
        task_type: str,
        session_id: str,
        agent_type: str,
        schedule_time: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Schedule a new task"""
        task_id = str(uuid.uuid4())
        
        # Parse schedule time
        if schedule_time:
            try:
                run_date = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
            except ValueError:
                run_date = datetime.now() + timedelta(minutes=1)  # Default to 1 minute from now
        else:
            run_date = datetime.now() + timedelta(minutes=1)
        
        # Create task info
        task_info = {
            'task_id': task_id,
            'task_type': task_type,
            'session_id': session_id,
            'agent_type': agent_type,
            'parameters': parameters or {},
            'created_at': datetime.now().isoformat(),
            'scheduled_for': run_date.isoformat(),
            'status': 'scheduled'
        }
        
        # Store task
        self.tasks[task_id] = task_info
        
        # Schedule the task
        try:
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=DateTrigger(run_date=run_date),
                args=[task_id],
                id=task_id,
                name=f"{task_type}_{agent_type}_{session_id}",
                replace_existing=True
            )
            
            task_info['status'] = 'scheduled'
            logger.info(f"Task {task_id} scheduled for {run_date}")
            
        except Exception as e:
            task_info['status'] = 'failed'
            task_info['error'] = str(e)
            logger.error(f"Failed to schedule task {task_id}: {str(e)}")
        
        return task_id
    
    def _execute_task(self, task_id: str):
        """Execute a scheduled task"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return
        
        task_info = self.tasks[task_id]
        task_info['status'] = 'running'
        task_info['started_at'] = datetime.now().isoformat()
        
        try:
            # Get the appropriate agent
            agent = self.agent_factory.get_agent(task_info['agent_type'])
            
            # Execute based on task type
            result = None
            if task_info['task_type'] == 'file_analysis':
                result = self._execute_file_analysis(agent, task_info)
            elif task_info['task_type'] == 'audit_report':
                result = self._execute_audit_report(agent, task_info)
            elif task_info['task_type'] == 'tax_calculation':
                result = self._execute_tax_calculation(agent, task_info)
            elif task_info['task_type'] == 'consultation':
                result = self._execute_consultation(agent, task_info)
            else:
                result = self._execute_custom_task(agent, task_info)
            
            # Update task status
            task_info['status'] = 'completed'
            task_info['result'] = result
            task_info['completed_at'] = datetime.now().isoformat()
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            task_info['status'] = 'failed'
            task_info['error'] = str(e)
            task_info['failed_at'] = datetime.now().isoformat()
            logger.error(f"Task {task_id} failed: {str(e)}")
    
    def _execute_file_analysis(self, agent, task_info):
        """Execute file analysis task"""
        parameters = task_info['parameters']
        file_path = parameters.get('file_path')
        file_name = parameters.get('file_name')
        
        if not file_path or not file_name:
            raise ValueError("file_path and file_name required for file_analysis task")
        
        return agent.analyze_file(file_name, file_path, task_info['session_id'])
    
    def _execute_audit_report(self, agent, task_info):
        """Execute audit report generation task"""
        parameters = task_info['parameters']
        audit_type = parameters.get('audit_type', 'financial')
        
        prompt = f"Generate a comprehensive {audit_type} audit report based on previous analysis."
        return agent.chat(prompt, task_info['session_id'])
    
    def _execute_tax_calculation(self, agent, task_info):
        """Execute tax calculation task"""
        parameters = task_info['parameters']
        tax_year = parameters.get('tax_year', datetime.now().year)
        
        prompt = f"Perform tax calculations and optimization analysis for {tax_year}."
        return agent.chat(prompt, task_info['session_id'])
    
    def _execute_consultation(self, agent, task_info):
        """Execute consultation task"""
        parameters = task_info['parameters']
        consultation_topic = parameters.get('topic', 'general financial consultation')
        
        prompt = f"Provide consultation on: {consultation_topic}"
        return agent.chat(prompt, task_info['session_id'])
    
    def _execute_custom_task(self, agent, task_info):
        """Execute custom task"""
        parameters = task_info['parameters']
        custom_prompt = parameters.get('prompt', 'Please provide analysis')
        
        return agent.chat(custom_prompt, task_info['session_id'])
    
    def _daily_audit_summary(self):
        """Daily audit summary task"""
        logger.info("Executing daily audit summary task")
        # This would generate summaries for all active audit sessions
        # Implementation depends on your specific requirements
        
    def _weekly_tax_check(self):
        """Weekly tax compliance check"""
        logger.info("Executing weekly tax compliance check")
        # This would check tax compliance for all active sessions
        
    def _monthly_consultant_report(self):
        """Monthly consultant report"""
        logger.info("Executing monthly consultant report")
        # This would generate monthly reports for all consultant sessions
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a specific session"""
        return [
            task for task in self.tasks.values() 
            if task['session_id'] == session_id
        ]
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        try:
            if task_id in self.tasks:
                task_info = self.tasks[task_id]
                if task_info['status'] == 'scheduled':
                    self.scheduler.remove_job(task_id)
                    task_info['status'] = 'cancelled'
                    task_info['cancelled_at'] = datetime.now().isoformat()
                    logger.info(f"Task {task_id} cancelled")
                    return True
                else:
                    logger.warning(f"Cannot cancel task {task_id} with status {task_info['status']}")
                    return False
            else:
                logger.warning(f"Task {task_id} not found")
                return False
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False
    
    def reschedule_task(self, task_id: str, new_schedule_time: str) -> bool:
        """Reschedule an existing task"""
        try:
            if task_id not in self.tasks:
                logger.warning(f"Task {task_id} not found")
                return False
            
            task_info = self.tasks[task_id]
            if task_info['status'] != 'scheduled':
                logger.warning(f"Cannot reschedule task {task_id} with status {task_info['status']}")
                return False
            
            # Parse new schedule time
            try:
                run_date = datetime.fromisoformat(new_schedule_time.replace('Z', '+00:00'))
            except ValueError:
                logger.error(f"Invalid schedule time format: {new_schedule_time}")
                return False
            
            # Remove old job and schedule new one
            self.scheduler.remove_job(task_id)
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=DateTrigger(run_date=run_date),
                args=[task_id],
                id=task_id,
                name=task_info.get('name', f"Task_{task_id}"),
                replace_existing=True
            )
            
            # Update task info
            task_info['scheduled_for'] = run_date.isoformat()
            task_info['rescheduled_at'] = datetime.now().isoformat()
            
            logger.info(f"Task {task_id} rescheduled for {run_date}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reschedule task {task_id}: {str(e)}")
            return False
