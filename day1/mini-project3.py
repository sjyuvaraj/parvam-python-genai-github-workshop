# Todo List
def todo_manager(todo_list, *tasks, **actions):
    for task in tasks:
        todo_list.append([task, "pending"])
        print(f"➕ Added: {task}")


    if actions.get('remove'):
        for task in actions['remove']:
            todo_list[:] = [t for t in todo_list if t[0] != task]
            print(f"❌ Removed: {task}")


    if actions.get('complete'):
        for task in todo_list:
            if task[0] in actions['complete']:
                task[1] = "done"
                print(f"✅ Completed: {task[0]}")


    print("\n📋 Current Tasks:")
    for task, status in todo_list:
        print(f" [{status}] {task}")


my_tasks = []
todo_manager(my_tasks, "Learn Python", "Learn Python OOPs", "Learn Django", "Play Games", complete=["Learn Python"], remove=["Play Games"])