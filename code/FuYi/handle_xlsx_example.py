import fuyi_log_xlsx as log_xlsx


# 调用插入数据函数
log_xlsx.insert_log_data(
    task_name="新示例任务",
    time="2025-05-08",
    data_fetch_success=True,
    cloud_path="new_cloud/path/data",
    copy_success=True,
    local_path="new_local/path/data", 
    table_change_success=True,
    db_insert_success=True
)

# 调用检查数据获取状态函数
status_list = log_xlsx.check_data_fetch_status(DEFAULT_SAVE_PATH, '数据获取是否成功')
print(status_list)