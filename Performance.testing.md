# Performance Testing

性能测试方法。

- [Performance Testing](#performance-testing)
  - [HiBench](#hibench)
  - [系统能力检测](#系统能力检测)
    - [UADK 及 硬件加速器](#uadk-及-硬件加速器)
    - [I/O 设备，磁盘](#io-设备磁盘)
  - [TeraSort Benchmark](#terasort-benchmark)
    - [准备工作：设定 HDFS Transparent Encryption 模式](#准备工作设定-hdfs-transparent-encryption-模式)
    - [`teragen` `terasort` 命令行使用举例](#teragen-terasort-命令行使用举例)
    - [Terasort 2.4GB 数据 (24M rows)](#terasort-24gb-数据-24m-rows)
    - [Terasort 25GB 数据 (256M rows)](#terasort-25gb-数据-256m-rows)
    - [Terasort 100GB 数据 (1G rows)](#terasort-100gb-数据-1g-rows)

## HiBench

编译命令：

    git clone https://github.com/Intel-bigdata/HiBench.git HiBench.git
    cd HiBench.git
    mvn -Phadoopbench -Dspark=2.4 -Dscala=2.11 clean package
        ... ...
        [INFO] ------------------------------------------------------------------------
        [INFO] Reactor Summary:
        [INFO]
        [INFO] hibench 8.0-SNAPSHOT ............................... SUCCESS [  0.135 s]
        [INFO] hibench-common 8.0-SNAPSHOT ........................ SUCCESS [ 49.875 s]
        [INFO] HiBench data generation tools 8.0-SNAPSHOT ......... SUCCESS [01:58 min]
        [INFO] hadoopbench 8.0-SNAPSHOT ........................... SUCCESS [  0.003 s]
        [INFO] hadoopbench-sql 8.0-SNAPSHOT ....................... SUCCESS [  05:15 h]
        [INFO] mahout 8.0-SNAPSHOT ................................ SUCCESS [  02:03 h]
        [INFO] PEGASUS: A Peta-Scale Graph Mining System 2.0-SNAPSHOT SUCCESS [ 13.317 s]
        [INFO] nutchindexing 8.0-SNAPSHOT ......................... SUCCESS [  04:14 h]
        [INFO] sparkbench 8.0-SNAPSHOT ............................ SUCCESS [  0.009 s]
        [INFO] sparkbench-common 8.0-SNAPSHOT ..................... SUCCESS [ 15.235 s]
        [INFO] sparkbench micro benchmark 8.0-SNAPSHOT ............ SUCCESS [  8.194 s]
        [INFO] sparkbench machine learning benchmark 8.0-SNAPSHOT . SUCCESS [ 32.744 s]
        [INFO] sparkbench-websearch 8.0-SNAPSHOT .................. SUCCESS [  4.131 s]
        [INFO] sparkbench-graph 8.0-SNAPSHOT ...................... SUCCESS [  7.727 s]
        [INFO] sparkbench-sql 8.0-SNAPSHOT ........................ SUCCESS [  9.951 s]
        [INFO] sparkbench project assembly 8.0-SNAPSHOT ........... SUCCESS [ 16.059 s]
        [INFO] flinkbench 8.0-SNAPSHOT ............................ SUCCESS [  0.003 s]
        [INFO] flinkbench-streaming 8.0-SNAPSHOT .................. SUCCESS [ 33.173 s]
        [INFO] gearpumpbench 8.0-SNAPSHOT ......................... SUCCESS [  0.003 s]
        [INFO] gearpumpbench-streaming 8.0-SNAPSHOT ............... SUCCESS [ 13.274 s]
        [INFO] stormbench 8.0-SNAPSHOT ............................ SUCCESS [  0.003 s]
        [INFO] stormbench-streaming 8.0-SNAPSHOT .................. SUCCESS [ 11.749 s]
        [INFO] ------------------------------------------------------------------------
        [INFO] BUILD SUCCESS
        [INFO] ------------------------------------------------------------------------
        [INFO] Total time:  11:38 h
        [INFO] Finished at: 2024-04-03T00:38:49+08:00
        [INFO] ------------------------------------------------------------------------

## 系统能力检测

### UADK 及 硬件加速器

    while true; do echo "$(date +'%y/%m/%d %H:%M:%S ') Run:" && sleep 5 && cat /sys/kernel/debug/hisi_sec2/*/qm/regs | grep QM_DFX_DB_CNT && echo ""; done

### I/O 设备，磁盘

    sudo yum install -yq sysstat iotop
    iostat -m -p nvme0n1 nvme1n1 nvme2n1 nvme3n1 10
    iotop -d 10

## TeraSort Benchmark

### 准备工作：设定 HDFS Transparent Encryption 模式

TeraSort把测试数据存放在统一的目录中。为了比较使用硬件加速后的效果，需要首先将测试目录指定为加密目录（i.e. encrption zone）。命令参考如下，此处以 `/zone2` 举例，`gd0325.1619`是加密密钥名称。

    # hadoop key create gd0325.1619
    # hadoop fs -mkdir /zone2
    # hdfs crypto -createZone -keyName gd0325.1619 -path /zone2

关于如何使用TeraSort，可以参考这里的简化脚本：

    git clone https://github.com/sunileman/MapReduce-Performance_Testing TeraSort.testing.git

### `teragen` `terasort` 命令行使用举例

举例，生成 100GB 数据 (1G row)

    hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-*examples*.jar \
        teragen \
        -Dmapred.map.tasks=95 \
        `expr 1024 \* 1024 \* 1024` \
        /zone2/terasort-input

建议的 TeraGen task 数量为核数减一。`-Dmapred.map.task=(vcpu numbers - 1)`

    hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-*examples*.jar \
        terasort \
        -Dmapred.reduce.tasks=48 \
        /zone2/terasort-input \
        /zone2/terasort-output
    
    hadoop fs -rm -f -r /zone2/terasort-output

建议的 TeraSort task 数量为核数的一半。`-Dmapred.reduce.task=(vcpu numbers divided by 2)`

### Terasort 2.4GB 数据 (24M rows)

KAEProvider + UADK:

    sed -i 's/BC/KAEProvider/g' etc/hadoop/core-site.xml 
    hadoop fs -rm -f -r /zone2/terasort-output
    time hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-*examples*.jar  terasort -Dmapred.reduce.tasks=48 /zone2/terasort-input /zone2/terasort-output
    
    real    1m26.101s
    user    1m55.372s
    sys     0m15.341s

    real    1m28.176s
    user    2m0.581s
    sys     0m16.241s

    real    1m25.257s
    user    1m42.370s
    sys     0m15.169s

    real    1m26.243s
    user    1m47.133s
    sys     0m15.143s

BC:

    sed -i 's/KAEProvider/BC/g' etc/hadoop/core-site.xml 

    real    1m54.501s
    user    2m43.461s
    sys     0m14.087s

    real    1m56.346s
    user    2m51.848s
    sys     0m14.831s

    real    1m55.491s
    user    2m53.159s
    sys     0m15.617s

cat /sys/class/uacce/hisi_sec*/device/numa_node

### Terasort 25GB 数据 (256M rows)

    hadoop fs -rm -f -r /zone2/terasort-input
    hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-*examples*.jar  teragen -Dmapred.map.tasks=95 `expr 256 \* 1024 \* 1024` /zone2/terasort-input

KAEProvider + UADK:

    sed -i 's/BC/KAEProvider/g' $HADOOP_HOME/etc/hadoop/core-site.xml 
    hadoop fs -rm -f -r /zone2/terasort-output
    time hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-*examples*.jar  terasort -Dmapred.reduce.tasks=48 /zone2/terasort-input /zone2/terasort-output

    real    14m0.594s
    user    14m0.104s
    sys     2m6.624s

    real    13m51.222s
    user    13m50.860s
    sys     2m12.218s

BC:

    sed -i 's/KAEProvider/BC/g' $HADOOP_HOME/etc/hadoop/core-site.xml 
    hadoop fs -rm -f -r /zone2/terasort-output
    time hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-*examples*.jar  terasort -Dmapred.reduce.tasks=48 /zone2/terasort-input /zone2/terasort-output

    real    18m59.101s
    user    22m36.986s
    sys     1m52.592s

### Terasort 100GB 数据 (1G rows)

    hadoop fs -rm -f -r /zone2/terasort-input
    hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-*examples*.jar  teragen -Dmapred.map.tasks=95 `expr 1024 \* 1024 \* 1024` /zone2/terasort-input

KAEProvider + UADK:

    sed -i 's/BC/KAEProvider/g' $HADOOP_HOME/etc/hadoop/core-site.xml 

    hadoop fs -rm -f -r /zone2/terasort-output
    time \
        hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-*examples*.jar \
            terasort \
            -Dmapred.reduce.tasks=48 \
            /zone2/terasort-input \
            /zone2/terasort-output

    real    91m26.321s
    user    82m31.546s

BC:

    sed -i 's/KAEProvider/BC/g' $HADOOP_HOME/etc/hadoop/core-site.xml 
    hadoop fs -rm -f -r /zone2/terasort-output
    time \
        hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-*examples*.jar \
            terasort \
            -Dmapred.reduce.tasks=48 \
            /zone2/terasort-input \
            /zone2/terasort-output

    real    135m47.011s
    user    143m39.925s
    sys     6m34.882s

typical CPU load average (in 5 minutes): 1.32+