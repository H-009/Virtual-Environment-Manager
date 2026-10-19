<p align="center">
  <img width="18%" align="center" src="https://raw.githubusercontent.com/H-009/Virtual-Environment-Manager/main/VEM.png" alt="logo">
</p>
  <h1 align="center">
  Virtual-Environment-Manager
</h1>
<p align="center">
  基于QFluentWidgets实现的可视化半自动Python虚拟环境管理器
</p>


<div align="center">

[![GPLv3](https://img.shields.io/badge/License-GPLv3-blue?color=#4ec820)](LICENSE)
[![Version](https://img.shields.io/github/v/release/H-009/Virtual-Environment-Manager?color=%2334D058&label=Version)](https://github.com/H-009/Virtual-Environment-Manager/releases)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows&logoColor=white)](https://www.microsoft.com/windows)

</div>

## 运行
克隆这个仓库，进入VEM文件夹后在终端中执行以下命令：
```shell
python VEM.py
```

## 安装
前往 [Releases 页面](https://github.com/H-009/Virtual-Environment-Manager/releases/latest) 下载最新版本的安装包

## 使用手册
VEM提供更美观的环境管理界面<br>
侧边导航栏包含多种按钮实现跳转到所需界面

### 环境
导航栏-环境 显示创建过的环境<br>
并对支持的环境(例如venv)开启CMD电源 如开启自动进入环境 VEM会自动执行启动参数进入环境<br>
环境控制栏 提供对环境CMD的不同操作:
- 电源：对CMD执行开启关闭操作
- 图钉：执行添加后的自动命令
- 预设脚本：执行补全参数后的命令
- 手动更新：强制刷新CMD
- 弹出：CMD取消嵌入状态
- 重启：执行关闭与开启操作
- 全屏：将CMD设为全屏独占

### 控制台
导航栏-控制台 提供与虚拟环境CMD不同的CMD<br>
控制台提供独立的CMD 不使用任何启动参数 适用于手动输入命令的场景<br>
控制台侧边控制栏 提供对控制台CMD的不同操作：
- 激活：激活控制台
- 销毁：销毁当前控制台
- 控制台列表：显示全部已激活的控制台
- 手动更新：同环境CMD 强制刷新CMD
- 弹出： 同环境CMD CMD取消嵌入状态
- 上一个：上一个控制台
- 下一个：下一个控制台
- 重启：同环境CMD 执行关闭与开启操作
- 全屏：同环境CMD 将CMD设为全屏独占

### 管理
导航栏-图钉 预设脚本 配置文件 提供各项的表格管理<br>
包含各种基础操作：复制 刷新 删除详情

导航栏-虚拟环境 便携式环境 基础环境 提供环境各项的表格管理
- 虚拟环境：包含基础操作与 编辑名称与启动参数 打开环境位置 卸载与删除条目
- 便携式环境：包含基础操作与 删除条目
- 基础环境：包含基础操作与 编辑名称 打开环境位置 删除条目

### 创建
导航栏-创建 提供多种创建 包括：
- 虚拟环境：Python Virtual Environment‌ 标准虚拟环境
- 便携式环境：Python Embeddable Package 嵌入式环境
- 基础环境：标准Python环境
- 配置文件：包含多命令的自动输入
- 预设脚本：带参数的自动命令
- 图钉：自动命令

### 下载
导航栏-下载 提供更便捷的方式下载Python安装包：
<br>
获取所需版本的可用文件后不同的下载项提供不同方式下载<br>
如默认站点下载速度慢 设置-下载-资源站 支持更换清华镜像站与华为镜像站

- 添加到下载列表：加入到下载列表进行后台下载
- 立即下载：打开下载对话框进行下载 并显示进度与速度
- 外部下载：跳转到默认浏览器下载

### 安装
导航栏-安装 提供下载后的安装包快速安装：
<br>
根据不同安装模式提供安装包路径或提供安装包参数后激活安装包<br>
- 快速：提供与Python默认值相反的参数选项

不同安装方式所执行的操作不一：
- 激活：根据当前模式与参数执行安装命令
- 手动激活：直接运行目标安装包

### 下载列表
导航栏-下载列表 显示后台中的下载任务队列

### 设置
导航栏-设置 包含大量自定义配置项 包括但不限于：
- 主题：主题模式 强调色 云母效果 懒加载
- CMD：嵌入时长 自动进入环境 监控频率 回调时长 弹出坐标等
- 缩放：DPI缩放 非整数缩放 高DPI像素映射
- 窗口：启动时全屏 启动后全屏 启动后最大化
- 启动页面：启动页面动画全屏 启动页面图标大小 图标阴影
- 下载：下载路径 最大并行下载数 资源站 站点同步 补全器等
- 通知：脱控通知 被动关机通知
- 提示：开机提示 关机提示 激活提示 销毁提示 切换提示
- 音效：开启音效 禁用警告音效 禁用操作音效 禁用下载完成音效等
- 关于：CMD QFluentWidgets PyQt5 Python MetaverseSDK 版本等
- 配置：配置文件 跳过退出保存 配置文件保护 演示模式 强制退出等
- 备份：备份路径 完整备份 备份配置
- 恢复：恢复备份 自动重载 自动退出
- 同步：同步路径 同步本地 同步配置 自动备份同步 同步重载
- 池：落盘池 重载池 排序池 配置池 CMD池 图标池 图像池 矢量图池等

## 许可证
VEM采用`GPLv3`许可证开源