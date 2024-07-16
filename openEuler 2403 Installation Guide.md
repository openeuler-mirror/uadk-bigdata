# 通过MobaXterm远程安装openEuler 24.03 指南

## 目录

- [环境](#环境)
- [准备工作](#准备工作)
- [远程连接到服务器](#远程连接到服务器)
- [下载 openEuler 24.03 ISO 镜像](#下载-openeuler-2403-iso-镜像)
- [上传 ISO 镜像到服务器](#上传-iso-镜像到服务器)
- [挂载 openEuler 24.03 ISO 镜像](#挂载-openeuler-2403-iso-镜像)
- [安装 openEuler 24.03](#安装-openeuler-2403)
- [配置系统](#配置系统)
- [完成安装](#完成安装)

---

## 环境

- **目标操作系统**：openEuler 24.03 LTS版本
- **硬件配置**：TaiShan 200 (Model 2280) (VD)服务器
- **工具**：MobaXterm

## 准备工作

确保已完成以下准备工作：

- 登录uniVPN连接IP
- 下载并安装 MobaXterm 客户端：[MobaXterm官网](https://mobaxterm.mobatek.net/download.html)。
- 获得远程服务器的IP地址（管理IP）、用户名和密码。

## 远程连接到服务器

打开 MobaXterm，并按照以下步骤连接到服务器：

- 点击上方的 "Session"（会话）按钮。
- 在弹出的窗口中选择 "SSH" 会话类型。
- 在 "Remote host"（远程主机）栏中输入服务器的IP地址（管理IP）。
- 在 "Specify username"（指定用户名）栏中输入您的用户名。（默认管理员账户为“root”）
- 点击 "OK" 连接到服务器，然后输入密码以完成连接。

## 下载 openEuler 24.03 ISO 镜像

- 在本地计算机上，打开浏览器并下载 openEuler 24.03 的 ISO 镜像文件：[下载地址](https://www.openeuler.org/zh/download/archive/detail/?version=openEuler%2024.03%20LTS)。

- 架构选择“AArch64”，场景选择“服务器”，在内存允许的情况下可选择Offline Everything ISO（离线完整版）。

- 解压下载文件
  
## 上传 ISO 镜像到服务器

 使用 MobaXterm 将下载好的 ISO 镜像上传到远程服务器：

- 点击左侧状态栏的“地球”图标（SFTP）。
- 点击绿色箭头（Upload to current folder）。
- 在本地计算机中找到已下载的 openEuler 24.03 的 ISO 镜像文件。

## 挂载 openEuler 24.03 ISO 镜像

在服务器上，执行以下命令来挂载 ISO 镜像到系统：

```bash
# 创建用于挂载ISO的目录
sudo mkdir /mnt/iso

# 挂载ISO文件到创建的目录
sudo mount -o loop /path/to/openEuler-24.03.iso /mnt/iso 
```

其中“/path/to/openEuler-24.03.iso”替换为ISO的实际文件路径

## 安装 openEuler 24.03

ISO镜像挂载完成后，进入挂载目录并执行安装脚本：

```bash
# 进入挂载目录
cd /mnt/iso

# 运行安装脚本
sudo ./install.sh
```

安装过程可能会要求进行一些配置，如分区、用户设置等。

## 配置系统

安装完成后，根据系统提示进行必要的配置，包括但不限于：

```bash
# 设置系统语言和时区
sudo dpkg-reconfigure tzdata

# 创建用户账号和密码
sudo adduser username
sudo passwd username
```

## 完成安装

安装和配置完成后，根据安装程序的指示重启服务器。安装过程中可能需要在服务器的控制台（MobaXterm 的会话窗口）上进行一些额外的配置和确认操作。
