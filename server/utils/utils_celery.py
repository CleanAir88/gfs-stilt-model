from celery.task.control import inspect

def get_queue_length(queue_name='celery'):
    """
    获取指定队列中的任务总数（包括活动、保留和计划中的任务）
    
    Args:
        queue_name: 队列名称，默认是'celery'
        
    Returns:
        int: 队列中的任务总数
    """
    inspector = inspect()
    
    # 获取不同状态的任务
    active_tasks = inspector.active() or {}
    reserved_tasks = inspector.reserved() or {}
    scheduled_tasks = inspector.scheduled() or {}
    
    # 计算总任务数
    queue_length = 0
    
    # 统计活动任务
    for worker, tasks in active_tasks.items():
        queue_length += len([t for t in tasks if t.get('delivery_info', {}).get('routing_key') == queue_name])
    
    # 统计保留任务
    for worker, tasks in reserved_tasks.items():
        queue_length += len([t for t in tasks if t.get('delivery_info', {}).get('routing_key') == queue_name])
    
    # 统计计划任务
    for worker, tasks in scheduled_tasks.items():
        queue_length += len([t for t in tasks if t.get('delivery_info', {}).get('routing_key') == queue_name])
    
    return queue_length

def get_task_count_by_name(task_name):
    """
    获取指定任务名称的任务数量
    
    Args:
        task_name: 任务的完整路径名称，例如'apps.model_gfs_stilt.tasks.run_gfs_stilt_task'
        
    Returns:
        int: 指定名称的任务数量
    """
    inspector = inspect()
    
    # 获取不同状态的任务
    active_tasks = inspector.active() or {}
    reserved_tasks = inspector.reserved() or {}
    scheduled_tasks = inspector.scheduled() or {}
    
    # 计算指定任务名称的任务数
    task_count = 0
    
    # 统计活动任务
    for worker, tasks in active_tasks.items():
        task_count += len([t for t in tasks if t['name'] == task_name])
    
    # 统计保留任务
    for worker, tasks in reserved_tasks.items():
        task_count += len([t for t in tasks if t['name'] == task_name])
    
    # 统计计划任务
    for worker, tasks in scheduled_tasks.items():
        task_count += len([t for t in tasks if t['name'] == task_name])
    
    return task_count