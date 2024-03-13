# 介绍

本文介绍 Hadoop，HBase，以及 KMS 服务相关信息。在本实验中使用的软件版本分别是：

1. Hadoop: v3.4
2. HBase: v2.5.7
3. JDK: v8.0

## hadoop 配置文件路径名

    /usr/local/hadoop/etc/hadoop/hdfs-site.xml

## 环境设置 /etc/profile

    # tail /etc/profile
    export HADOOP_HOME=/usr/local/hadoop
    export PATH=${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${PATH}
    export HBASE_HOME=/usr/local/hbase
    export PATH=${HBASE_HOME}/bin:${PATH}
    export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.382.b05-6.oe2309.aarch64/jre/
    export PATH=${JAVA_HOME}/bin:${PATH}

## Datanode

    # lsblk
    NAME               MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
    nvme0n1            259:0    0   1.5T  0 disk /srv/BigData/hadoop/data1
    nvme1n1            259:1    0   2.9T  0 disk /srv/BigData/hadoop/data2
    nvme2n1            259:2    0   1.5T  0 disk /srv/BigData/hadoop/data3
