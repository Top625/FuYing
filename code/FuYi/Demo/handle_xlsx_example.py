import fuyi_log_xlsx as log_xlsx

# 调用插入数据函数
log_xlsx.insert_log_data(
    task_name="任务2",
    time="2025-05-09",
    data_fetch_success=False,
    cloud_path="cloud/path/data",
    copy_success=False,
    local_path="local/path/data", 
    table_change_success=False,
    db_insert_success=False
)

# 调用检查数据获取状态函数
status_list = log_xlsx.check_data_fetch_status(log_xlsx.DEFAULT_SAVE_PATH, '复制到本地是否成功')
print("数据获取状态列表:", status_list)

# # 更新日志数据
# log_xlsx.update_log_data(
#     task_name="任务2",
#     time="2025-05-09",
#     data_fetch_success=True,
#     cloud_path="updated_cloud/path/data",
#     copy_success=False,
#     local_path="",
#     table_change_success=False,
#     db_insert_success=False
# )