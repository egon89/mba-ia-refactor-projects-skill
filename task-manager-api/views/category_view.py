def category_list_item(category, task_count):
    data = category.to_dict()
    data['task_count'] = task_count
    return data
