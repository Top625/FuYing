# coding=utf-8

# 同花顺财经早餐
# 首页  热点新闻

# http://news.10jqka.com.cn/hotnews_list/


import os
import re
import bs4
import time
import pandas
import datetime
import pypyodbc
import requests
import model_function as mf
import model_configuration as mc

con = mc.con
channel = mc.channel
chrome_driver = mc.chrome_driver


sql_table_name = "Event_DailyNews_Pool"
end_date = datetime.date.today()
begin_date = mf.tradedays_offset(channel, -2, end_date)


########################################################################################################################
# sql_table_name = "Event_DailyNews_P111"
# end_date = datetime.date(2021, 6, 11)
# begin_date = datetime.date(2024, 5, 1)
# begin_date = end_date
########################################################################################################################


columns_data_frame = pandas.DataFrame(
    [
        ["Date", "varchar(20)", "", "", "日期"],
        ["Code", "varchar(10)", "", "", "代码"],
        ["Source", "varchar(150)", "", "", "来源"],
    ], columns=["sql列名", "sql数据类型", "sql主键", "英文名称", "中文名称"])
# mf.sql_check_table(channel, sql_table_name, columns_data_frame, p_sql_primary_key="1")  # 通过参数来确定是不是添加主键
mf.sql_check_table(channel, sql_table_name, columns_data_frame, p_sql_primary_key="")  # 不设置主键


def html_10jqka_data():
    pass
    # 模拟浏览器
    v_headers_request_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}


    v_cmd_empty = "select * from " + sql_table_name + " where Date = 'yyyy-mm-dd'"
    v_data_frame_empty = pandas.read_sql(v_cmd_empty, con)

    for p in range(1,5):
        if p == 1:
            v_html_url = "http://news.10jqka.com.cn/hotnews_list/"
        else:
            v_html_url = "http://news.10jqka.com.cn/hotnews_list/index_" + str(p) + ".shtml"
        # v_html_raw = requests.get(v_html_url, headers=v_headers_request_headers)
        v_html_raw = mf.html_requests(v_html_url, "1")
        v_html_bs4 = bs4.BeautifulSoup(v_html_raw, "html.parser")
        v_html_content = v_html_bs4.find(class_="list-con")  # 获取指定范围内的文本内容
        v_html_list_cjzc = v_html_content.find_all("a", text=re.compile("财经早餐"))  # 挑选出符合条件的内容
        for m in range(len(v_html_list_cjzc)):
            # v_html_list_cjzc[0].find_next("span")  # 几月几日 时分
            v_html_title = v_html_list_cjzc[m].get("title")
            v_html_href = v_html_list_cjzc[m].get("href")

            v_sql_date = str(datetime.datetime.strptime((v_html_href.split("/")[-2]), "%Y%m%d").date())


            v_children_html_raw = mf.html_requests(v_html_href, "1")
            v_children_html_bs4 = bs4.BeautifulSoup(v_children_html_raw, "html.parser")
            v_children_html_content = v_children_html_bs4.find(class_="main-text atc-content")
            v_children_html_single_stock = v_children_html_content.find_all("a", class_="singleStock")
            for n in range(len(v_children_html_single_stock)):
                v_html_code = v_children_html_single_stock[n].get("onmouseover").split(",")[-2]
                v_sql_code = (v_html_code.split("_")[-1]  + "." + v_html_code.split("_")[0].upper()).replace("'", "")
                v_data_frame_empty.loc[len(v_data_frame_empty)] = [v_sql_date, v_sql_code, v_html_title]
            v_data_frame_empty = v_data_frame_empty.drop_duplicates()

        # 当页最后一条数据的日期
        v_html_page_end_date = v_html_content.find_all("span", class_="arc-title")[-1].find("a").get("href").split("/")[-2]
        if str(datetime.datetime.strptime(v_html_page_end_date, "%Y%m%d").date()) <= str(begin_date):
            break

    if v_data_frame_empty.__len__() >0:
        mf.data_frame_write_sql(channel, sql_table_name, v_data_frame_empty)


def main():
    html_10jqka_data()


if __name__ == '__main__':
    pass

    # main()


    # 正式使用
    program_file_path_name = __file__  # 程序文件路径名称
    program_file_name = os.path.basename(__file__)  # 程序文件名称
    mf.logging_replace_print_main(main, __file__)


    # program_file_path_name = __file__  # 程序文件路径名称
    # logger = mf.logging_replace_print(program_file_path_name)  # 记录日志
    # logger.info("")
    # # logger.info(os.environ['COMPUTERNAME'])  # 电脑名称
    #
    # print("程序【开始时间】：" + str(datetime.datetime.now()))
    # logger.info("程序【开始时间】")
    #
    # try:
    #     main()
    #     pass
    # except Exception as e:
    #     # logger.error(e)
    #
    #     # traceback.print_exc()
    #     logger.error(traceback.format_exc())
    #
    # print("程序【结束时间】：" + str(datetime.datetime.now()))
    # logger.info("程序【结束时间】\n")