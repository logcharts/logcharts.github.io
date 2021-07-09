# 日志图表

## 简介

通过python脚本,分析日志成分,表页面展示分析结果

## 示例

https://logcharts.github.io

## 使用方法

```shell
wget https://logcharts.github.io/LogFileAnalizer.py
python LogFileAnalizer.py your-project.log
```
* 分析完成后会显示分析结果url, 浏览器直接访问即可.

* url有效期为24小时,分析页面可 导入/导出 分析结果json.

* 如果正则没有匹配到日志格式,可自行修改py脚本里的正则.