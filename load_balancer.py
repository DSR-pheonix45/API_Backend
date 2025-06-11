"""
Load Balancer for HF DABBY system
Distributes API requests optimally among the agents
Implements round-robin, least-connections, and weighted algorithms
"""

import time
import threading
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from agent_factory import AgentFactory
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"

@dataclass
class AgentInstance:
    """Represents an agent instance with load balancing metrics"""
    agent_id: str
    agent_type: str
    agent: Any
    weight: int = 1
    active_connections: int = 0
    total_requests: int = 0
    total_response_time: float = 0.0
    last_used: float = 0.0
    health_status: str = "healthy"
    created_at: float = 0.0

class LoadBalancer:
    """Load balancer for distributing requests among agents"""
    
    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self.agent_pools: Dict[str, List[AgentInstance]] = defaultdict(list)
        self.agent_factory = AgentFactory()
        self.round_robin_counters: Dict[str, int] = defaultdict(int)
        self.lock = threading.RLock()
        
        # Agent weights for weighted round robin
        self.agent_weights = {
            "Dabby Consultant": 3,  # Higher weight for general consultant
            "Auditor Agent": 2,     # Medium weight for auditor
            "Tax Agent": 2          # Medium weight for tax agent
        }
        
        # Initialize agent pools
        self._initialize_agent_pools()
        
        # Health check configuration
        self.health_check_interval = 60  # seconds
        self.max_response_time = 30.0   # seconds
        self.max_connections_per_agent = 10
        
        # Start health checker
        self._start_health_checker()
    
    def _initialize_agent_pools(self):
        """Initialize agent pools with default instances"""
        agent_types = ["Dabby Consultant", "Auditor Agent", "Tax Agent"]
        
        for agent_type in agent_types:
            # Create initial instances (can be scaled based on load)
            initial_instances = 2 if agent_type == "Dabby Consultant" else 1
            
            for i in range(initial_instances):
                self._create_agent_instance(agent_type)
    
    def _create_agent_instance(self, agent_type: str) -> AgentInstance:
        """Create a new agent instance"""
        agent = self.agent_factory.get_agent(agent_type)
        agent_id = f"{agent_type}_{len(self.agent_pools[agent_type])}"
        
        instance = AgentInstance(
            agent_id=agent_id,
            agent_type=agent_type,
            agent=agent,
            weight=self.agent_weights.get(agent_type, 1),
            created_at=time.time()
        )
        
        with self.lock:
            self.agent_pools[agent_type].append(instance)
        
        logger.info(f"Created agent instance: {agent_id}")
        return instance
    
    def get_agent(self, agent_type: str = "Dabby Consultant") -> Any:
        """Get an agent instance using the configured load balancing algorithm"""
        with self.lock:
            if agent_type not in self.agent_pools or not self.agent_pools[agent_type]:
                # Create agent pool if it doesn't exist
                self._create_agent_instance(agent_type)
            
            instances = [inst for inst in self.agent_pools[agent_type] if inst.health_status == "healthy"]
            
            if not instances:
                logger.warning(f"No healthy instances available for {agent_type}")
                # Fallback: create a new instance
                instance = self._create_agent_instance(agent_type)
                instances = [instance]
            
            # Select instance based on algorithm
            selected_instance = self._select_instance(instances, agent_type)
            
            # Update metrics
            selected_instance.active_connections += 1
            selected_instance.total_requests += 1
            selected_instance.last_used = time.time()
            
            return selected_instance.agent
    
    def _select_instance(self, instances: List[AgentInstance], agent_type: str) -> AgentInstance:
        """Select an instance based on the configured algorithm"""
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin_select(instances, agent_type)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections_select(instances)
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(instances, agent_type)
        elif self.algorithm == LoadBalancingAlgorithm.RESPONSE_TIME:
            return self._response_time_select(instances)
        else:
            return instances[0]  # Fallback
    
    def _round_robin_select(self, instances: List[AgentInstance], agent_type: str) -> AgentInstance:
        """Round robin selection"""
        counter = self.round_robin_counters[agent_type]
        selected = instances[counter % len(instances)]
        self.round_robin_counters[agent_type] = (counter + 1) % len(instances)
        return selected
    
    def _least_connections_select(self, instances: List[AgentInstance]) -> AgentInstance:
        """Least connections selection"""
        return min(instances, key=lambda x: x.active_connections)
    
    def _weighted_round_robin_select(self, instances: List[AgentInstance], agent_type: str) -> AgentInstance:
        """Weighted round robin selection"""
        # Calculate total weight
        total_weight = sum(inst.weight for inst in instances)
        
        # Use counter to determine selection
        counter = self.round_robin_counters[agent_type]
        target = counter % total_weight
        
        current_weight = 0
        for instance in instances:
            current_weight += instance.weight
            if target < current_weight:
                self.round_robin_counters[agent_type] += 1
                return instance
        
        # Fallback
        return instances[0]
    
    def _response_time_select(self, instances: List[AgentInstance]) -> AgentInstance:
        """Response time based selection"""
        def avg_response_time(instance):
            if instance.total_requests == 0:
                return 0.0
            return instance.total_response_time / instance.total_requests
        
        return min(instances, key=avg_response_time)
    
    def release_agent(self, agent_type: str, response_time: float = 0.0):
        """Release an agent instance and update metrics"""
        with self.lock:
            if agent_type in self.agent_pools:
                # Find the most recently used instance
                instances = self.agent_pools[agent_type]
                if instances:
                    # Find instance with the most recent last_used time
                    recent_instance = max(instances, key=lambda x: x.last_used)
                    
                    # Update metrics
                    recent_instance.active_connections = max(0, recent_instance.active_connections - 1)
                    recent_instance.total_response_time += response_time
    
    def add_agent_instance(self, agent_type: str, weight: int = 1) -> str:
        """Add a new agent instance to the pool"""
        instance = self._create_agent_instance(agent_type)
        instance.weight = weight
        return instance.agent_id
    
    def remove_agent_instance(self, agent_type: str, agent_id: str) -> bool:
        """Remove an agent instance from the pool"""
        with self.lock:
            if agent_type in self.agent_pools:
                instances = self.agent_pools[agent_type]
                for i, instance in enumerate(instances):
                    if instance.agent_id == agent_id:
                        # Wait for active connections to finish
                        if instance.active_connections > 0:
                            logger.warning(f"Removing instance {agent_id} with {instance.active_connections} active connections")
                        
                        instances.pop(i)
                        logger.info(f"Removed agent instance: {agent_id}")
                        return True
        return False
    
    def scale_up(self, agent_type: str, instances_to_add: int = 1):
        """Scale up the agent pool"""
        for _ in range(instances_to_add):
            self.add_agent_instance(agent_type)
        logger.info(f"Scaled up {agent_type} pool by {instances_to_add} instances")
    
    def scale_down(self, agent_type: str, instances_to_remove: int = 1):
        """Scale down the agent pool"""
        with self.lock:
            if agent_type in self.agent_pools:
                instances = self.agent_pools[agent_type]
                
                # Don't scale below 1 instance
                if len(instances) <= instances_to_remove:
                    logger.warning(f"Cannot scale down {agent_type} below 1 instance")
                    return
                
                # Remove instances with least connections first
                instances_sorted = sorted(instances, key=lambda x: x.active_connections)
                
                for i in range(instances_to_remove):
                    if i < len(instances_sorted):
                        instance_to_remove = instances_sorted[i]
                        self.remove_agent_instance(agent_type, instance_to_remove.agent_id)
                
                logger.info(f"Scaled down {agent_type} pool by {instances_to_remove} instances")
    
    def auto_scale(self):
        """Auto-scale agent pools based on load"""
        with self.lock:
            for agent_type, instances in self.agent_pools.items():
                if not instances:
                    continue
                
                # Calculate average load
                total_connections = sum(inst.active_connections for inst in instances)
                avg_connections = total_connections / len(instances)
                
                # Scale up if average connections > 70% of max
                if avg_connections > self.max_connections_per_agent * 0.7:
                    if len(instances) < 5:  # Max 5 instances per type
                        self.scale_up(agent_type, 1)
                
                # Scale down if average connections < 30% of max and more than 1 instance
                elif avg_connections < self.max_connections_per_agent * 0.3 and len(instances) > 1:
                    self.scale_down(agent_type, 1)
    
    def _health_check_instance(self, instance: AgentInstance):
        """Perform health check on an agent instance"""
        try:
            # Simple health check - try to create a basic response
            start_time = time.time()
            
            # Test agent availability (this is a simple test)
            if hasattr(instance.agent, 'name'):
                _ = instance.agent.name
            
            response_time = time.time() - start_time
            
            # Check response time threshold
            if response_time > self.max_response_time:
                instance.health_status = "unhealthy"
                logger.warning(f"Agent {instance.agent_id} health check failed: slow response")
            else:
                instance.health_status = "healthy"
            
            # Check connection count
            if instance.active_connections > self.max_connections_per_agent:
                instance.health_status = "overloaded"
                logger.warning(f"Agent {instance.agent_id} is overloaded")
        
        except Exception as e:
            instance.health_status = "unhealthy"
            logger.error(f"Agent {instance.agent_id} health check failed: {str(e)}")
    
    def _health_checker(self):
        """Background health checker"""
        while True:
            try:
                time.sleep(self.health_check_interval)
                
                with self.lock:
                    for agent_type, instances in self.agent_pools.items():
                        for instance in instances:
                            self._health_check_instance(instance)
                
                # Auto-scale based on load
                self.auto_scale()
                
            except Exception as e:
                logger.error(f"Health checker error: {str(e)}")
    
    def _start_health_checker(self):
        """Start the background health checker thread"""
        health_thread = threading.Thread(target=self._health_checker, daemon=True)
        health_thread.start()
        logger.info("Health checker started")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        stats = {}
        
        with self.lock:
            for agent_type, instances in self.agent_pools.items():
                type_stats = {
                    "instance_count": len(instances),
                    "healthy_instances": len([i for i in instances if i.health_status == "healthy"]),
                    "total_connections": sum(i.active_connections for i in instances),
                    "total_requests": sum(i.total_requests for i in instances),
                    "average_response_time": 0.0,
                    "instances": []
                }
                
                # Calculate average response time
                total_time = sum(i.total_response_time for i in instances)
                total_requests = sum(i.total_requests for i in instances)
                if total_requests > 0:
                    type_stats["average_response_time"] = total_time / total_requests
                
                # Instance details
                for instance in instances:
                    instance_stats = {
                        "agent_id": instance.agent_id,
                        "weight": instance.weight,
                        "active_connections": instance.active_connections,
                        "total_requests": instance.total_requests,
                        "health_status": instance.health_status,
                        "last_used": instance.last_used,
                        "avg_response_time": (
                            instance.total_response_time / instance.total_requests 
                            if instance.total_requests > 0 else 0.0
                        )
                    }
                    type_stats["instances"].append(instance_stats)
                
                stats[agent_type] = type_stats
        
        return stats
    
    def set_algorithm(self, algorithm: LoadBalancingAlgorithm):
        """Change the load balancing algorithm"""
        self.algorithm = algorithm
        logger.info(f"Load balancing algorithm changed to: {algorithm.value}")
    
    def set_agent_weight(self, agent_type: str, weight: int):
        """Set weight for an agent type"""
        self.agent_weights[agent_type] = weight
        
        # Update existing instances
        with self.lock:
            if agent_type in self.agent_pools:
                for instance in self.agent_pools[agent_type]:
                    instance.weight = weight
        
        logger.info(f"Weight for {agent_type} set to {weight}")
