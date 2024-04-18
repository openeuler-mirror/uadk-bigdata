# OpenSSL 3.0 Load-Balancer 测试场景

- [OpenSSL 3.0 Load-Balancer 测试场景](#openssl-30-load-balancer-测试场景)
  - [在 Docker Container 中 OpenSSL 3.0 编译 和 安装](#在-docker-container-中-openssl-30-编译-和-安装)
    - [使用`pkg-config`验证 OpenSSL 3.0 和 UADK 的安装](#使用pkg-config验证-openssl-30-和-uadk-的安装)
  - [在 Docker Container 中 uadk\_provider 编译 和 安装](#在-docker-container-中-uadk_provider-编译-和-安装)
  - [配置环境变量](#配置环境变量)
  - [验证 uadk\_provider](#验证-uadk_provider)
    - [uadk\_provider 能支持的算法有哪些？](#uadk_provider-能支持的算法有哪些)
  - [场景一：使用 `openssl speed` 验证 SM4-CTR 用 default 还是 uadk\_provier 更快？](#场景一使用-openssl-speed-验证-sm4-ctr-用-default-还是-uadk_provier-更快)
  - [场景二：SM4](#场景二sm4)

本文介绍为 OpenSSL 3.0 开发的多算力平台场景动态负载平衡的测试场景。

ldprov 提供一个通用的动态负载均衡能力。本文以两个算法在鲲鹏平台上的多算力实现，介绍其功能及用法。

涉及到的软件仓库，分别在 gitee.com 和 github.com 同步存放。

## 在 Docker Container 中 OpenSSL 3.0 编译 和 安装

    ./Configure enable-md2
    make -s -j 100
    make test TESTS='test_evp_libctx test_provider' V=1
    make test TESTS='test_provider' V=1
    make doc-nits

    sudo make -j 100 install


### 使用`pkg-config`验证 OpenSSL 3.0 和 UADK 的安装

    $ export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig/  
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
    $ ./configure
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

    $ sudo chmod 777 /dev/hisi*
    $ ls -lat /dev/hisi*
    $ export WD_RSA_CTX_NUM="sync:2@0,async:4@0"
    $ export WD_DH_CTX_NUM="sync:2@0,async:4@0"
    $ export WD_CIPHER_CTX_NUM="sync:2@2,async:4@2"
    $ export WD_DIGEST_CTX_NUM="sync:2@2,async:4@2"

## 验证 uadk_provider

### uadk_provider 能支持的算法有哪些？

    $ /usr/local/bin/openssl list -provider uadk_provider -all-algorithms | grep uadk
        { 1.3.14.3.2.26, SHA-1, SHA1, SSL3-SHA1 } @ uadk_provider
        { 1.2.156.10197.1.401, SM3 } @ uadk_provider
        { 1.2.840.113549.2.5, MD5, SSL3-MD5 } @ uadk_provider
        SHA2-224 @ uadk_provider
        SHA2-256 @ uadk_provider
        SHA2-384 @ uadk_provider
        SHA2-512 @ uadk_provider
        { 2.16.840.1.101.3.4.1.2, AES-128-CBC, AES128 } @ uadk_provider
        { 2.16.840.1.101.3.4.1.22, AES-192-CBC, AES192 } @ uadk_provider
        { 2.16.840.1.101.3.4.1.42, AES-256-CBC, AES256 } @ uadk_provider
        { 1.3.111.2.1619.0.1.1, AES-128-XTS } @ uadk_provider
        { 1.3.111.2.1619.0.1.2, AES-256-XTS } @ uadk_provider
        { 2.16.840.1.101.3.4.1.1, AES-128-ECB } @ uadk_provider
        { 2.16.840.1.101.3.4.1.21, AES-192-ECB } @ uadk_provider
        { 2.16.840.1.101.3.4.1.41, AES-256-ECB } @ uadk_provider
        { 1.2.156.10197.1.104.1, SM4-ECB } @ uadk_provider
        { 1.2.156.10197.1.104.2, SM4, SM4-CBC } @ uadk_provider
        { 1.2.156.10197.1.104.7, SM4-CTR } @ uadk_provider
        { 1.2.840.113549.3.7, DES-EDE3-CBC, DES3 } @ uadk_provider
        { DES-EDE3, DES-EDE3-ECB } @ uadk_provider
        { 1.2.840.113549.1.1.1, 2.5.8.1.1, RSA, rsaEncryption } @ uadk_provider
        { 1.2.840.113549.1.1.1, 2.5.8.1.1, RSA, rsaEncryption } @ uadk_provider
        { 1.2.840.113549.1.3.1, DH, dhKeyAgreement } @ uadk_provider
        Name: uadk RSA Keymgmt implementation.
            IDs: { 1.2.840.113549.1.1.1, 2.5.8.1.1, RSA, rsaEncryption } @ uadk_provider
            IDs: { 1.2.840.113549.1.3.1, DH, dhKeyAgreement } @ uadk_provider

## 场景一：使用 `openssl speed` 验证 SM4-CTR 用 default 还是 uadk_provier 更快？

综合测试对比 uadk_provider vs. default:

    openssl speed -provider uadk_provider -provider default -async_jobs 1 -evp sm4-cbc
    openssl speed -provider default -async_jobs 1 -evp sm4-cbc
    openssl speed -provider uadk_provider -provider default -async_jobs 1 -evp sm4-ctr
    openssl speed -provider default -async_jobs 1 -evp sm4-ctr

    TODO：【2023/09】能看出uadk_provider测得的数据, sm4-cbc / sm4-ctr 提高0.6~1倍，在起作用。

## 场景二：SM4
