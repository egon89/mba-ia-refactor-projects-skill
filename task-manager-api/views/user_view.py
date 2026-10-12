def user_list_item(user, task_count):
    data = user.to_dict()
    data['task_count'] = task_count
    return data


def user_detail(user, tasks):
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in tasks]
    return data
