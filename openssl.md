# OpenSSL 3.0 Load-Balancer 测试场景

本文介绍为 OpenSSL 3.0 开发的多算力平台场景动态负载平衡的测试场景。

ldprov 提供一个通用的动态负载均衡能力。本文以两个算法在鲲鹏平台上的多算力实现，介绍其功能及用法。

涉及到的软件仓库，分别在 gitee.com 和 github.com 同步存放。

## 在 Docker Container 中 OpenSSL 3.0 编译 和 安装

### 使用`pkg-config`验证 OpenSSL 3.0 和 UADK 的安装

    $ pkg-config libcrypto --libs
    -L/usr/local/lib -lcrypto
    
    $ pkg-config libwd --libs
    -L/usr/local/lib -lwd

## 在 Docker Container 中 uadk_provider 编译 和 安装

从这里下载 uadk_provider 代码：<https://github.com/Linaro/uadk_engine>，并根据页面介绍进行编译和安装。

    $ git clone https://github.com/Linaro/uadk_engine.git uadk_engine.git
    $ cd uadk_engine.git/
    $ ls
    $ git status
    $ autoreconf -i
    $ make
    $ sudo make install

从这里查看编译的结果：

    $ ls -lat /usr/local/lib/ossl-modules/uadk_provider.*
    -rw-r--r--. 1 root root 735748 Mar 11 10:15 uadk_provider.a
    -rwxr-xr-x. 1 root root   1088 Mar 11 10:15 uadk_provider.la
    lrwxrwxrwx. 1 root root     22 Mar 11 10:15 uadk_provider.so -> uadk_provider.so.1.3.0
    lrwxrwxrwx. 1 root root     22 Mar 11 10:15 uadk_provider.so.1 -> uadk_provider.so.1.3.0
    -rwxr-xr-x. 1 root root 419992 Mar 11 10:15 uadk_provider.so.1.3.0

在验证 uadk_provider 功能之前，请先确认下面的环境变量已经设置。

## 配置环境变量

    $ export LD_LIBRARY_PATH=/usr/local/lib
    $ export OPENSSL_MODULES=/usr/local/lib/ossl-modules

    $ sudo chmod 666 /dev/hisi*
    $ ls -lat /dev/hisi*
    $ export WD_RSA_CTX_NUM="sync:2@0,async:4@0"
    $ export WD_DH_CTX_NUM="sync:2@0,async:4@0"
    $ export WD_CIPHER_CTX_NUM="sync:2@2,async:4@2"
    $ export WD_DIGEST_CTX_NUM="sync:2@2,async:4@2"

## 验证 uadk_provider

    $ /usr/local/bin/openssl list -provider uadk_provider -all-algorithms | grep uadk

    $ /usr/local/bin/openssl speed -provider uadk_provider -provider default -evp sm4-ecb
    Doing SM4-ECB for 3s on 16 size blocks: 2022035 SM4-ECB's in 2.74s
    Doing SM4-ECB for 3s on 64 size blocks: 1874565 SM4-ECB's in 2.69s
    Doing SM4-ECB for 3s on 256 size blocks: 1488854 SM4-ECB's in 2.80s
    Doing SM4-ECB for 3s on 1024 size blocks: 829540 SM4-ECB's in 2.89s
    Doing SM4-ECB for 3s on 8192 size blocks: 162752 SM4-ECB's in 2.96s
    Doing SM4-ECB for 3s on 16384 size blocks: 84966 SM4-ECB's in 2.99s
    version: 3.2.0-dev
    built on: Mon Mar 11 07:41:34 2024 UTC
    options: bn(64,64)
    compiler: gcc -fPIC -pthread -Wa,--noexecstack -Wall -O0 -g -DOPENSSL_USE_NODELETE -DOPENSSL_PIC -DOPENSSL_BUILDING_OPENSSL
    CPUINFO: OPENSSL_armcap=0xbd
    The 'numbers' are in 1000s of bytes per second processed.
    type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
    SM4-ECB          11807.50k    44599.32k   136123.79k   293926.98k   450427.16k   465579.58k

## 场景一：MD5

## 场景二：SM4
