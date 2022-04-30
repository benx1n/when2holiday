# when2holiday
定时提醒摸鱼小助手<br>
摸！大！鱼！<br>
本插件部分代码参考了[HMScygnet](https://github.com/HMScygnet)大佬的[假期查询插件](https://github.com/pcrbot/holiday)
## 部署

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/benx1n/when2holiday`
2. 在项目文件夹下执行`pip install -r requirements.txt`安装依赖
3. 在`./config.json`中修改自定义文本
4. 在 `config/__bot__.py`的模块列表里加入 `when2holiday`
5. 重启hoshinoBot
6. 本插件默认开启，如不需要请在lssv中禁用本模块即可

## 指令

|  指令   | 必要参数  |可选参数|说明|
|  :----  | :----  | :---- |:----|
| **测试假期推送**|**日期**||测试指定日期的推送，日期格式如2022-06-01|
| **剩余假期** |无||查看剩余假期|


## 效果
<div align="left">
  <img src="https://s1.ax1x.com/2022/04/25/Lo5w7D.jpg" width="300" />
</div>

## TODO
- [ ] 按群自定义推送消息结构
