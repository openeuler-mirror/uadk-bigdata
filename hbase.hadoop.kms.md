# 介绍

- [介绍](#介绍)
  - [hadoop 配置文件路径名](#hadoop-配置文件路径名)
  - [环境设置 /etc/profile](#环境设置-etcprofile)
  - [Datanode](#datanode)
  - [JRE 和 JAVA\_HOME 设置](#jre-和-java_home-设置)
  - [重要目录](#重要目录)
  - [在 HDFS Transparent Encryption 中使用 SM4 算法](#在-hdfs-transparent-encryption-中使用-sm4-算法)
    - [hadoop.security.crypto.codec.classes.EXAMPLECIPHERSUITE](#hadoopsecuritycryptocodecclassesexampleciphersuite)
    - [hadoop.security.crypto.codec.classes.sm4.ctr.nopadding](#hadoopsecuritycryptocodecclassessm4ctrnopadding)
    - [hadoop.security.crypto.cipher.suite](#hadoopsecuritycryptociphersuite)
    - [hadoop.security.crypto.jce.provider](#hadoopsecuritycryptojceprovider)
    - [hadoop.security.crypto.buffer.size](#hadoopsecuritycryptobuffersize)
  - [Hadoop, HBase 服务启动和停止](#hadoop-hbase-服务启动和停止)
    - [启动](#启动)
    - [停止](#停止)
    - [多节点集群部署的 start/stop 脚本](#多节点集群部署的-startstop-脚本)
  - [Hadoop / HDFS 验证测试](#hadoop--hdfs-验证测试)
  - [测试用例：a oneliner](#测试用例a-oneliner)
  - [`hbase pe` 命令提示](#hbase-pe-命令提示)
  - [如何确认 UADK / uacce 硬件加速器被使用？](#如何确认-uadk--uacce-硬件加速器被使用)
  - [Hadoop, HBase and Zookeeper 涉及的 Java 进程](#hadoop-hbase-and-zookeeper-涉及的-java-进程)
    - [__HBase__ processes](#hbase-processes)
    - [__Zookeeper__ process](#zookeeper-process)
    - [__Hadoop__ processes](#hadoop-processes)

本文介绍 Hadoop，HBase，以及 KMS 服务相关信息。在本实验中使用的软件版本分别是：

1. Hadoop: v3.4.0-RC3
2. HBase: v2.5.7
3. JDK: Bisheng JDK 1.8.0 - u402

Hadoop 3.4-RC3: https://github.com/apache/hadoop/releases/tag/release-3.4.0-RC3

HBase 2.5.7: https://github.com/apache/hbase/releases/tag/rel%2F2.5.7

注意：Hadoop 3.4 版本才有 SM4 的支持。

如何搭建 Hadoop cluster，请参考[Hadoop Cluster Setup](https://apache.github.io/hadoop/hadoop-project-dist/hadoop-common/ClusterSetup.html)，以及[Hadoop: Setting up a Single Node Cluster](https://apache.github.io/hadoop/hadoop-project-dist/hadoop-common/SingleCluster.html)。

如何配置 Hadoop KMS 服务，请参考[这里](https://github.com/liusheng/liusheng.github.io/issues/14)。

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

可用磁盘 SSD disks 三块，如下：

    # lsblk
    NAME               MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
    nvme0n1            259:0    0   1.5T  0 disk /srv/BigData/hadoop/data1
    nvme1n1            259:1    0   2.9T  0 disk /srv/BigData/hadoop/data2
    nvme2n1            259:2    0   1.5T  0 disk /srv/BigData/hadoop/data3

## JRE 和 JAVA_HOME 设置

这个 JRE 是原始版本的 BiSheng JDK 1.8.0-u382，用于对比测试：

    export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.382.b05-6.oe2309.aarch64/jre

    ./bin/java -version
        openjdk version "1.8.0_382"
        OpenJDK Runtime Environment Bisheng (build 1.8.0_382-b05)
        OpenJDK 64-Bit Server VM Bisheng (build 25.382-b05, mixed mode)

这个 JRE 是支持 UADK Provider 的JDK，基于 Bisheng JDK 1.8.0-u402：

    export JAVA_HOME=/usr/lib/jvm/jre-bisheng-jdk8u402-kaeprovider-ossl3.0

    ./bin/java -version
        openjdk version "1.8.0_402-internal"
        OpenJDK Runtime Environment  (build 1.8.0_402-internal-root_2024_03_24_05_12-b00)
        OpenJDK 64-Bit Server VM  (build 25.402-b00, mixed mode)

要使用某一个JRE，这些文件中包含`JAVA_HOME`环境变量的设置。需要同步修改，添加：

1. `${HADOOP_HOME}/etc/hadoop/hadoop-env.sh`
2. `${HBASE_HOME}/conf/hbase-env.sh`
3. `/etc/profile`

## 重要目录

1. Hadoop, HDFS, KMS 配置：

    ${HADOOP_HOME}/etc/hadoop/core-site.xml

1. HBase 配置：

    ${HBASE_HOME}/conf/hbase-site.xml

1. HBase Log 保存在如下目录：

    hbase/logs

## 在 HDFS Transparent Encryption 中使用 SM4 算法

为了使用SM4作为HDFS透明加密功能的缺省算法，需要在`core-site.xml`中添加：

    <property>
        <name>hadoop.security.crypto.cipher.suite</name>
        <value>SM4/CTR/NoPadding</value>
    </property>
    <property>
        <name>hadoop.security.crypto.codec.classes.sm4.ctr.nopadding</name>
        <value>org.apache.hadoop.crypto.JceSm4CtrCryptoCodec</value>
    <property>

这里要注意，尽管`hadoop.security.crypto.codec.classes.sm4.ctr.nopadding`的缺省值是OpenSSL，但是因为算法兼容原因，不能使用。需要设置为 `JceSm4CtrCryptoCodec`。

以下是相关参数说明。参考[Selecting an encryption algorithm and codec](https://apache.github.io/hadoop/hadoop-project-dist/hadoop-hdfs/TransparentEncryption.html#Selecting_an_encryption_algorithm_and_codec)。

### hadoop.security.crypto.codec.classes.EXAMPLECIPHERSUITE

The prefix for a given crypto codec, contains a comma-separated list of implementation classes for a given crypto codec (eg EXAMPLECIPHERSUITE). The first implementation will be used if available, others are fallbacks.

### hadoop.security.crypto.codec.classes.sm4.ctr.nopadding

Default: org.apache.hadoop.crypto.OpensslSm4CtrCryptoCodec, org.apache.hadoop.crypto.JceSm4CtrCryptoCodec

Comma-separated list of crypto codec implementations for SM4/CTR/NoPadding. The first implementation will be used if available, others are fallbacks.

### hadoop.security.crypto.cipher.suite

Default: AES/CTR/NoPadding

Cipher suite for crypto codec, now AES/CTR/NoPadding and SM4/CTR/NoPadding are supported.

    conf.get(HADOOP_SECURITY_CRYPTO_CIPHER_SUITE_KEY, HADOOP_SECURITY_CRYPTO_CIPHER_SUITE_DEFAULT);

### hadoop.security.crypto.jce.provider

Default: None

The JCE provider name used in CryptoCodec.

    import static org.apache.hadoop.fs.CommonConfigurationKeysPublic.HADOOP_SECURITY_CRYPTO_JCE_PROVIDER_KEY

Refer to definition in: `hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/CommonConfigurationKeysPublic.java`

    /**
     * @see
     * <a href="{@docRoot}/../hadoop-project-dist/hadoop-common/core-default.xml">
     * core-default.xml<a>
     */
    public static final String HADOOP_SECURITY_CRYPTO_JCE_PROVIDER_KEY =
        "hadoop.security.crypto.jce.provider";

### hadoop.security.crypto.buffer.size

Default: 8192

The buffer size used by CryptoInputStream and CryptoOutputStream.

## Hadoop, HBase 服务启动和停止

### 启动

    ${HADOOP_HOME}/sbin/start-all.sh
    hadoop --daemon start kms
    /usr/local/zookeeper/bin/zkServer.sh  start
    ${HBASE_HOME}/bin/start-hbase.sh

注意：启动后，通过如下命令判断来 Hbase 启动是否完成：

    curl -L http://localhost:16010/master-status | tee ms.html

### 停止

    ${HBASE_HOME}/bin/stop-hbase.sh
    /usr/local/zookeeper/bin/zkServer.sh  stop
    hadoop --daemon stop kms
    ${HADOOP_HOME}/sbin/stop-all.sh

### 多节点集群部署的 start/stop 脚本

    # ls
    mount.sh  start_hadoop.sh  stop_hadoop.sh
    # cat mount.sh
        #!/bin/sh

        ip_arr="agent1 agent2 agent3"
        function mount_disk(){
        for ip in $ip_arr
        do
            ssh $ip "sh /root/init.sh"
        done
        }

        mount_disk

    # cat start_hadoop.sh
        #!/bin/sh

        $HADOOP_HOME/sbin/start-all.sh
        $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver
        $HADOOP_HOME/bin/hadoop --daemon start kms

    # cat stop_hadoop.sh
        #!/bin/sh

        $HADOOP_HOME/sbin/stop-all.sh
        $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh stop historyserver
        $HADOOP_HOME/bin/hadoop --daemon stop kms

    # cat init_ssd.sh
        #!/bin/sh

        j=1
        for i in 0 2 3;do
                umount /dev/nvme${i}n1
                mkdir -p /srv/BigData/hadoop/data${j}
                #rm /home/hadoop -rf
                #mkfs.ext4 -F /dev/nvme${i}n1
                mount  /dev/nvme${i}n1 /srv/BigData/hadoop/data${j}
                j=$(($j+1))
        done

    # cat init.sh
        #!/bin/sh

        j=1
        for i in a b c d e f g h i j k l;do
                umount /dev/sd$i
                mkdir -p /srv/BigData/hadoop/data${j}
                #rm /home/hadoop -rf
        #        mkfs.ext4 -F /dev/sd$i
                mount  /dev/sd$i /srv/BigData/hadoop/data${j}
                j=$(($j+1))
        done

## Hadoop / HDFS 验证测试

各种命令的输出：

    # hadoop fs -ls /
    # hadoop fs -ls /zone1
    # hdfs crypto -listZones
    # hadoop key list
        Listing keys for KeyProvider: org.apache.hadoop.crypto.key.kms.LoadBalancingKMSClientProvider@387a8303
        gd0314.1558
        kmskey
        gd0325.1619
        key2
        key1

    # hdfs crypto -getFileEncryptionInfo -path /zone1/core-site.xml
        {cipherSuite: {name: SM4/CTR/NoPadding, algorithmBlockSize: 16}, cryptoProtocolVersion: CryptoProtocolVersion{description='Encryption zones', version=2, unknownValue=null}, edek: 08af03244604039ccee422c68bef8cbb, iv: 5306ad607bfc4dca6a8e86e19776e979, keyName: gd0314.1558, ezKeyVersionName: gd0314.1558@0}


    # hadoop key create gd0325.1619
        gd0325.1619 has been successfully created with options Options{cipher='SM4/CTR/NoPadding', bitLength=128, description='null', attributes=null}.
        org.apache.hadoop.crypto.key.kms.LoadBalancingKMSClientProvider@642a7222 has been updated.

    # hadoop fs -mkdir /zone2

    # hdfs crypto -createZone -keyName gd0325.1619 -path /zone2

    # hadoop fs -put ms.html /zone2
        2024-03-25 16:25:57,139 WARN crypto.JceSm4CtrCryptoCodec: no such algorithm: SHA1PRNG for provider BC

    # hadoop fs -cat /zone2/ms.html
        2024-03-25 16:30:58,822 WARN crypto.JceSm4CtrCryptoCodec: no such algorithm: SHA1PRNG for provider BC

        <!DOCTYPE html>
        <?xml version="1.0" encoding="UTF-8" ?>
        ... ...

    # hdfs crypto -getFileEncryptionInfo -path /zone2/ms.html
        {cipherSuite: {name: SM4/CTR/NoPadding, algorithmBlockSize: 16}, cryptoProtocolVersion: CryptoProtocolVersion{description='Encryption zones', version=2, unknownValue=null}, edek: cfeec4b81af045c86dd4915eddbc0eff, iv: 2a1dc46a428568bdee2a95894cc80a40, keyName: gd0325.1619, ezKeyVersionName: gd0325.1619@0}

## 测试用例：a oneliner

    # for i in {1..1}; do echo "Run $i:" && hadoop fs -rm /zone2/jre-bisheng-jdk8u402-kaeprovider-ossl3.0-0325.tar.gz || true && hadoop fs -put /usr/lib/jvm/jre-bisheng-jdk8u402-kaeprovider-ossl3.0-0325.tar.gz /zone2 && cat /sys/kernel/debug/hisi_sec2/*/qm/regs | grep QM_DFX_DB_CNT && echo ""; done

在执行这些操作之前和之后，查看加速器硬件寄存器 `QM_DFX_DB_CNT` 值的是否有变化，来判断 UADK 确实被使用。

## `hbase pe` 命令提示

    hbase pe --nomapred --size=10 --table=test10 --presplit=30  --compress='LZ4'  randomWrite 120

## 如何确认 UADK / uacce 硬件加速器被使用？

可以使用这个命令来查看 UADK/uacce 硬件加速器的计数器。通过对比前后两次读取的 QM_DFX_DB_CNT 寄存器值，可以知道是否有变化，变化了多少。从而确认 UADK / uacce 是否被使用。

    sudo su
    cat /sys/kernel/debug/hisi_sec2/*/qm/regs
    cat /sys/kernel/debug/hisi_sec2/*/qm/regs | grep QM_DFX_DB_CNT

## Hadoop, HBase and Zookeeper 涉及的 Java 进程

### __HBase__ processes

    __HMaster__: Manages the cluster metadata and assigns regions to region servers.

    __HRegionServer__: Stores and serves HBase data in its assigned region(s).

### __Zookeeper__ process

    __QuorumPeerMain__: Manages the Zookeeper quorum for HBase coordination. When you run HBase, it indirectly starts the QuorumPeerMain process as part of the Zookeeper integration within HBase.

### __Hadoop__ processes

    __ResourceManager__: Schedules and manages MapReduce and Spark jobs.

    __NodeManager__: Runs tasks assigned by the ResourceManager on each worker node.

    __NameNode__: Manages the file system namespace for HDFS (Hadoop Distributed File System).

    __SecondaryNameNode__: Periodically checkpoints the NameNode metadata.

    __DataNode__: Stores data blocks for HDFS across the cluster.

    __KMSWebServer__: Provides the web interface for the Key Management Service (KMS) used for securing HDFS data.