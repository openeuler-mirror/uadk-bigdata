# 自动化执行hbase pe测试

## 环境

- python3.9
- pandas，subprocess，re库

## 使用方法

1. 在script目录下的HbasePeTest.csv文件中按照相应的格式添加测试用例
2. 最重要的是在“Command”列中添加对应的命令
3. 添加完成后在命令行中使用python命令运行script目录下的main.py文件即可

## 测试环境

- 以上测试内容在以下平台上验证过

### 处理器

- HUAWEI Kunpeng 920 7260 * 2
- 单个处理器的主频：2600MHz
- 单个处理器的核数/线程数：64 cores/64 threads

### 内存

- Hynix DIMM000 32GB DDR4 2666MT/s * 8

### 储存

- MZ7LH960HAJR-00005 * 1
- ST1200MM0009 * 4

### 操作系统

- OpenEuler 24.03 LTS

### 运行环境

- Openjdk 1.8.0
- Hadoop 3.3.4
- Hbase 2.5.7

### 数据存放

- OpenEuler操作系统的根目录、启动分区和EFI系统分区位于硬盘SAMSUNG MZ7LH960HAJR-00005上
- Hbase以及Hadoop的数据存放在硬盘SAMSUNG MZ7LH960HAJR-00005的sdd3分区上
