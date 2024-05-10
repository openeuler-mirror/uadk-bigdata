# OpenSSL 3.0 Load-Balancer 测试场景

- [OpenSSL 3.0 Load-Balancer 测试场景](#openssl-30-load-balancer-测试场景)
  - [在 Docker Container 中 OpenSSL 3.0 编译 和 安装](#在-docker-container-中-openssl-30-编译-和-安装)
    - [使用`pkg-config`验证 OpenSSL 3.0 和 UADK 的安装](#使用pkg-config验证-openssl-30-和-uadk-的安装)
  - [在 Docker Container 中 uadk\_provider 编译 和 安装](#在-docker-container-中-uadk_provider-编译-和-安装)
  - [配置环境变量](#配置环境变量)
  - [验证 uadk\_provider](#验证-uadk_provider)
    - [uadk\_provider 能支持的算法有哪些？](#uadk_provider-能支持的算法有哪些)
  - [场景一：使用 `openssl speed` 验证 SM4-CTR 用 default 还是 uadk\_provider 更快？](#场景一使用-openssl-speed-验证-sm4-ctr-用-default-还是-uadk_provider-更快)
    - [async\_jobs 1](#async_jobs-1)
    - [async\_jobs 10](#async_jobs-10)
    - [multi 10](#multi-10)
    - [multi 10 with two hisi\_sec devices working in parallel](#multi-10-with-two-hisi_sec-devices-working-in-parallel)
    - [multi 20 with two hisi\_sec devices working in parallel](#multi-20-with-two-hisi_sec-devices-working-in-parallel)
    - [multi 40 with two hisi\_sec devices working in parallel](#multi-40-with-two-hisi_sec-devices-working-in-parallel)
    - [multi 60 with two hisi\_sec devices working in parallel](#multi-60-with-two-hisi_sec-devices-working-in-parallel)
    - [multi 80 with two hisi\_sec devices working in parallel](#multi-80-with-two-hisi_sec-devices-working-in-parallel)
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

## 场景一：使用 `openssl speed` 验证 SM4-CTR 用 default 还是 uadk_provider 更快？

综合测试对比 SM4-CTR 算法， uadk_provider vs. default 哪个更快:

    openssl speed -provider uadk_provider -provider default -async_jobs 1 -evp sm4-ctr
    cat /sys/kernel/debug/hisi_sec2/*/qm/regs | grep QM_DFX_DB_CNT
    openssl speed -provider default -async_jobs 1 -evp sm4-ctr
    cat /sys/kernel/debug/hisi_sec2/*/qm/regs | grep QM_DFX_DB_CNT

Note: `cat /sys/kernel/debug/hisi_sec2/*/qm/regs | grep QM_DFX_DB_CNT`

### async_jobs 1

    # openssl speed -provider default -async_jobs 1 -evp sm4-ctr
        Doing SM4-CTR for 3s on 16 size blocks: 6002423 SM4-CTR's in 2.99s
        Doing SM4-CTR for 3s on 64 size blocks: 5337232 SM4-CTR's in 3.00s
        Doing SM4-CTR for 3s on 256 size blocks: 2348146 SM4-CTR's in 3.00s
        Doing SM4-CTR for 3s on 1024 size blocks: 604520 SM4-CTR's in 3.00s
        Doing SM4-CTR for 3s on 8192 size blocks: 75727 SM4-CTR's in 2.99s
        Doing SM4-CTR for 3s on 16384 size blocks: 37875 SM4-CTR's in 3.00s
        version: 3.2.0-dev
        built on: Sun Mar 24 08:45:29 2024 UTC
        options: bn(64,64)
        compiler: gcc -fPIC -pthread -Wa,--noexecstack -Wall -O3 -DOPENSSL_USE_NODELETE -DOPENSSL_PIC -DOPENSSL_BUILDING_OPENSSL -DNDEBUG
        CPUINFO: OPENSSL_armcap=0xbd
        The 'numbers' are in 1000s of bytes per second processed.
        type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
        SM4-CTR          32119.99k   113860.95k   200375.13k   206342.83k   207476.78k   206848.00k

    # openssl speed -provider uadk_provider -provider default -async_jobs 1 -evp sm4-ctr
        type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
        SM4-CTR           3866.05k    15495.25k    62183.06k   237321.23k   456612.35k   471474.08k

### async_jobs 10

    # openssl speed -provider default -async_jobs 10 -evp sm4-ctr
        type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
        SM4-CTR          32012.54k   114239.17k   200504.06k   206341.80k   206779.73k   206787.93k

    # openssl speed -provider uadk_provider -provider default -async_jobs 10 -evp sm4-ctr
        type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
        SM4-CTR           5579.10k    17339.43k    52649.66k   196011.89k  1228592.55k  2281140.00k

### multi 10

    # openssl speed -provider default -multi 10 -seconds 120 -elapsed -evp sm4-ctr
        type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
        SM4-CTR         319949.11k  1138384.13k  2005259.69k  2062083.75k  2066989.06k  2067649.88k
        SM4-CTR         319931.07k  1137867.03k  2003471.89k  2061820.07k  2065891.87k  2066369.74k

    # openssl speed -provider uadk_provider -provider default -async_jobs 10 -multi 10 -evp sm4-ctr
        type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
        SM4-CTR          40662.10k   143187.75k   529901.48k  2818294.78k  3856102.74k  3849431.72k

### multi 10 with two hisi_sec devices working in parallel

    # openssl speed -provider uadk_provider -provider default -multi 10 -seconds 120 -evp sm4-ctr
        type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
        SM4-CTR          13500.34k    63651.29k   235971.03k   840059.72k  3034632.94k  3739119.34k
        SM4-CTR          13509.76k    57346.87k   222764.13k   788640.73k  2961521.60k  3670497.28k

    # openssl speed -provider uadk_provider -provider default -multi 10 -seconds 120 -elapsed -evp sm4-ctr
        type             16 bytes     64 bytes    256 bytes   1024 bytes   8192 bytes  16384 bytes
        SM4-CTR          17683.47k    63330.66k   241356.35k   839610.06k  3044970.84k  3711369.90k
        SM4-CTR           4231.23k    47430.67k    76532.02k   599274.04k  2591518.99k  3370097.60k
        SM4-CTR           4681.11k    42687.71k    78961.14k   578202.55k  2549159.66k  3327796.70k

### multi 20 with two hisi_sec devices working in parallel

    # openssl speed -provider default -multi 20 -seconds 20 -elapsed -evp sm4-ctr
        SM4-CTR         640019.85k  2276538.37k  4006128.86k  4124605.85k  4133664.36k  4134647.40k
        SM4-CTR         640069.68k  2274927.57k  4015306.61k  4122030.80k  4132623.56k  4134277.12k

    # openssl speed -provider uadk_provider -provider default -multi 20 -seconds 20 -elapsed -evp sm4-ctr
        SM4-CTR           7282.07k    60850.00k   149914.38k  1123897.45k  5156714.09k  6561099.68k
        SM4-CTR           7654.95k    50485.59k   143187.19k  1168020.43k  5131083.37k  6708602.47k

### multi 40 with two hisi_sec devices working in parallel

    # openssl speed -provider default -multi 40 -seconds 20 -elapsed -evp sm4-ctr
        SM4-CTR        1279971.26k  4552531.43k  8015539.14k  8248040.60k  8265528.52k  8268136.45k
        SM4-CTR        1279780.41k  4552059.69k  8048823.58k  8005700.04k  7924151.91k  7953707.83k

    # openssl speed -provider uadk_provider -provider default -multi 40 -seconds 20 -elapsed -evp sm4-ctr
        SM4-CTR          21306.24k    64037.45k   326836.94k  1621123.33k  7629483.40k  7756404.33k
        SM4-CTR          16398.13k    54053.68k   296889.87k  1859460.35k  7728587.57k  7756309.76k
        SM4-CTR          19884.44k    64849.51k   339523.41k  1564984.06k  7749677.47k  7756678.76k
        SM4-CTR          18531.02k    68479.91k   296649.13k  1631692.60k  7745306.62k  7756664.01k

### multi 60 with two hisi_sec devices working in parallel

    # openssl speed -provider default -multi 60 -seconds 20 -elapsed -evp sm4-ctr
        SM4-CTR        1919873.06k  6828072.19k 11419966.16k 11500206.03k 11561990.55k 11437108.19k
        SM4-CTR        1919545.31k  6686775.22k 10699080.42k 11070904.01k 11076703.03k 10980688.69k

    # openssl speed -provider uadk_provider -provider default -multi 60 -seconds 20 -elapsed -evp sm4-ctr
        SM4-CTR          25518.95k    79736.29k   363007.69k  1669525.25k  7752430.39k  7758521.96k
        SM4-CTR          22312.36k    66975.32k   323648.76k  1253113.96k  7753025.13k  7758765.62k
        SM4-CTR          23749.19k    73341.22k   364654.96k  1450117.68k  7752751.51k  7758544.69k
        SM4-CTR          26894.66k    84114.65k   344945.08k  1599865.31k  7753107.87k  7758792.98k

### multi 80 with two hisi_sec devices working in parallel

    # openssl speed -provider default -multi 80 -seconds 20 -elapsed -evp sm4-ctr
        SM4-CTR        2476187.60k  8013620.59k 12982942.26k 13367193.80k 13421463.70k 13401955.44k
        SM4-CTR        2440658.92k  7843174.65k 13100002.51k 13239890.89k 13205257.83k 13346893.00k

cpu load average 77%

    # openssl speed -provider uadk_provider -provider default -multi 80 -seconds 20 -elapsed -evp sm4-ctr
    ... uadk_err:  "do hw ciphers failed. "
        SM4-CTR          25791.72k    70921.82k   339090.87k  1352893.18k  7751837.70k  7759396.15k
        SM4-CTR          24297.16k    71918.61k   362315.88k  1366651.08k  7752460.29k  7759238.51k

Note: openssl speed usage,

    -multi num
        Run multiple operations in parallel.

    -async_jobs num
        Enable async mode and start specified number of jobs.

    -elapsed
        When calculating operations- or bytes‐per‐second, use wall‐clock time instead of CPU user time as divisor. It can be useful when testing speed of hardware engines.

    -seconds num
        Run benchmarks for num seconds.

    -bytes num
        Run benchmarks on num-byte buffers. Affects ciphers, digests and the CSPRNG.  The limit on the size of the buffer is INT_MAX - 64 bytes, which for a 32-bit int would be 2147483583 bytes.

## 场景二：SM4
