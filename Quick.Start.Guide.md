# 快速编译安装指南

- [快速编译安装指南](#快速编译安装指南)
  - [硬件和软件开发环境](#硬件和软件开发环境)
  - [BishengJDK 1.8.0 (含 KAEProvider)](#bishengjdk-180-含-kaeprovider)
    - [源代码下载](#源代码下载)
    - [编译环境](#编译环境)
    - [创建 docker container](#创建-docker-container)
    - [Boot JDK 和 JTReg 的准备](#boot-jdk-和-jtreg-的准备)
    - [编译命令](#编译命令)
    - [安装](#安装)
    - [修改 java.security，使能 KAEProvider](#修改-javasecurity使能-kaeprovider)
    - [测试验证](#测试验证)
  - [UADK](#uadk)
    - [源代码下载](#源代码下载-1)
    - [编译环境](#编译环境-1)
    - [编译命令](#编译命令-1)
    - [安装](#安装-1)
    - [测试验证](#测试验证-1)
  - [OpenSSL 3.0](#openssl-30)
    - [源代码下载](#源代码下载-2)
    - [编译环境](#编译环境-2)
    - [编译命令](#编译命令-2)
    - [安装](#安装-2)
    - [测试验证](#测试验证-2)
  - [UADK Provider for OpenSSL 3.0](#uadk-provider-for-openssl-30)
    - [源代码下载](#源代码下载-3)
    - [编译环境](#编译环境-3)
    - [编译命令](#编译命令-3)
    - [安装](#安装-3)
    - [测试验证](#测试验证-3)

这里介绍本实验的快速搭建步骤。如前面讲述，需要的软件模块包括：

1. BishengJDK 1.8.0 （含 KAEProvider）
1. UADK
1. OpenSSL 3.0
1. UADK Provider for OpenSSL 3.0

下面就依次介绍这几个模块的编译和安装。每个模块分为五个步骤介绍：源代码下载，编译环境，编译命令，安装 和 测试验证。

## 硬件和软件开发环境

本实验基于鲲鹏 Kunpeng 920 和 openEuler 23.09 OS 开发。

在实验开始前，需要确保鲲鹏920的硬件加速功能已经开启。请参考 [uadk.md](./uadk.md) 中 `在 Bootloader 中开启` 和 `内核启动参数 及 内核模块加载` 两节。

## BishengJDK 1.8.0 (含 KAEProvider)

### 源代码下载

私有源： https://gitee.com/docularxu/bishengjdk-8.git

Tag： [v1.01-jdk8u402-kaeprovider-ossl3.0](https://gitee.com/docularxu/bishengjdk-8/tree/v1.01-jdk8u402-kaeprovider-ossl3.0)

建议使用 Tag 版本。项目日常持续性开发使用的是这个分支：[working-jdk8u402-kaeprovider-ossl3.0](https://gitee.com/docularxu/bishengjdk-8/commits/working-jdk8u402-kaeprovider-ossl3.0)

### 编译环境

JDK的编译有很多的软件包依赖。为此创建 Dockerfile 方便统一创建环境。从[这里](https://github.com/docularxu/build-containers)获得编译需要的 Dockerfile。下面的步骤是基于这个 Dockerfile 的：`Dockerfile.ubuntu.2204.uadk-dev`。

### 创建 docker container

这里介绍用于 BishengJDK-1.8.0 编译的 docker container 的创建。参考 [README.md](https://github.com/docularxu/build-containers) 创建 docker image。

    docker build -f Dockerfile.ubuntu.2204.uadk-dev . -t uadk-jdk-dev:ubuntu.2204

基于此 docker image，使用所提供的脚本[`docker-run-uadk-dev.sh`](https://github.com/docularxu/build-containers) 创建 container。

    docker-run-uadk-dev.sh ubuntu-jdk-uadk <give_it_a_name>

### Boot JDK 和 JTReg 的准备

进入 docker container 之后，需要为后续编译准备`Boot JDK` 和 `JTReg`。这个步骤，请移步参考：[鉴于缺少Boot JDK](./BiShengJDK.md#鉴于缺少-boot-jdk)。

### 编译命令

注意：这里需要把下面 `./configure` 命令中的路径参数 `--with-jtreg` 和 `--with-boot-jdk` 替换为实际的安装路径，此处以`/home/guodong/`举例。

    unset JAVA_HOME
    make dist-clean   // optional
    bash ./configure --enable-kae \
            --with-extra-cflags='-Wno-error=nonnull' \
            --with-jtreg=/home/guodong/jtreg \
            --with-boot-jdk=/home/guodong/bisheng-jdk1.8.0_402
    make all JOBS=128

### 安装

编译好的 `JRE` image 位于源代码目录 `$BUILD/images/j2re-image`。

    $BUILD=./build/linux-aarch64-normal-server-release

需要把这个目录打包，然后解压到主机（即从 container 搬到 host 主机）的目标目录。在主机上，通常 JRE 会安装在：

    /usr/lib/jvm/[jre-version-name-string]

之后，环境变量 `JAVA_HOME` 设置为这个主机目标目录，便可以使用。

    export JAVA_HOME=/usr/lib/jvm/[jre-version-name-string]

### 修改 java.security，使能 KAEProvider

为了让 KAEProvider (基于 OpenSSL 3.0 和 UADK ) 成为 Java 程序 SM4 算法的首选 Provider，需要修改 `java.security`。

具体方法：通过修改`${JAVA_HOME}/lib/security/java.security`文件，添加 KAEProvider，并设置 KAEProvider 为最高优先级 (1最高):

    +    security.provider.1=org.openeuler.security.openssl.KAEProvider
    +    security.provider.2=sun.security.provider.Sun
    +    ... 依次设置其他 provider ...

### 测试验证

    # java -version
        openjdk version "1.8.0_402-internal"
        OpenJDK Runtime Environment  (build 1.8.0_402-internal-root_2024_03_29_02_25-b00)
        OpenJDK 64-Bit Server VM  (build 25.402-b00, mixed mode)

## UADK

### 源代码下载

代码仓库：https://github.com/docularxu/uadk

Tag：[v1.0-tag2.6-sm4-ctr](https://github.com/docularxu/uadk/releases/tag/v1.0-tag2.6-sm4-ctr)

建议使用 Tag 版本。项目日常持续性开发使用的是这个分支：[working-tag2.6-sm4-ctr](https://github.com/docularxu/uadk/commits/working-tag2.6-sm4-ctr/)

### 编译环境

在主机环境下用普通用户身份编译。

### 编译命令

    $ cd uadk.git
    $ ./cleanup.sh
    $ ./autogen.sh
    $ ./conf.sh
    $ make

### 安装

    $ sudo make install

这一步会把 UADK 库 (libwd.so etc.) 安装到目录 `/usr/local/lib` 和 `/usr/local/lib/uadk` 中。这两个目录路径后面会用到。

### 测试验证

在能够使用 UADK 功能之前，需要设置相关的环境变量。为了方便使用，环境变量（包括此处为 UADK 准备的，也包括下面 UADK Provider 以及 OpenSSL 3.0+ 相关）集中放在这个脚本文件里：[uadk-set-env.sh](https://github.com/docularxu/build-containers/blob/main/metadata/uadk-set-env.sh)。使用时，在当前环境下 `.  ` 运行（相当于`source`命令）将文件中的内容导入当前shell环境。

    $ . ./uadk-set-env.sh

UADK 测试命令，推荐使用 `uadk_tool`。前述步骤正常的话，它已经被安装到了 `/usr/local/bin` 之下。可直接运行。

    $ uadk_tool benchmark --alg sm4-128-ctr --mode sva --opt 0 --sync --pktlen 1024 --seconds 5 --multi 1 --thread 2 --ctxnum 6
    $ uadk_tool benchmark --alg sm4-128-ecb --mode sva --opt 0 --sync --pktlen 1024 --seconds 5 --multi 1 --thread 2 --ctxnum 6

## OpenSSL 3.0

### 源代码下载

代码仓库：https://github.com/docularxu/openssl.git

Tag：[v1.0-loadbalancer](https://github.com/docularxu/openssl/releases/tag/v1.0-loadbalancer)

建议使用 Tag 版本。项目日常持续性开发使用的是这个分支：[working-lb-on-master-rc5](https://github.com/docularxu/openssl/tree/working-lb-on-master-rc5)

### 编译环境

在主机环境下用普通用户身份编译。

    $ export LD_LIBRARY_PATH=/usr/local/lib
    $ export OPENSSL_MODULES=/usr/local/lib/ossl-modules

### 编译命令

    ./Configure enable-md2
    make -s -j 100

### 安装

    sudo make -j 100 install

这一步会把 OpenSSL 3.0+ 库 (libcrypto.so) 安装到目录 `/usr/local/lib`，这个目录路径后面会用到。

### 测试验证

首先参考 [uadk-set-env.sh](https://github.com/docularxu/build-containers/blob/main/metadata/uadk-set-env.sh) 确认 `${OPENSSL_MODULES}`, `${PKG_CONFIG_PATH}`, `${LD_LIBRARY_PATH}` 都有正确配置。

    $ pkg-config libwd --libs
        -L/usr/local/lib -lwd
    $ pkg-config libcrypto --libs
        -L/usr/local/lib -lcypto

    $ openssl version
        OpenSSL 3.2.0-dev  (Library: OpenSSL 3.2.0-dev )
    $ which openssl
        /usr/local/bin/openssl

## UADK Provider for OpenSSL 3.0

### 源代码下载

代码仓库：https://github.com/docularxu/uadk_engine 或者 https://gitee.com/docularxu/uadk_engine

Tag：[v1.0-tag1.3-sm4-ctr](https://github.com/docularxu/uadk_engine/releases/tag/v1.0-tag1.3-sm4-ctr)

建议使用 Tag 版本。项目日常持续性开发使用的是这个分支：[working_sm4_ctr](https://github.com/docularxu/uadk_engine/tree/working_sm4_ctr)

### 编译环境

在主机环境下用普通用户身份编译。

    $ export LD_LIBRARY_PATH=/usr/local/lib
    $ export OPENSSL_MODULES=/usr/local/lib/ossl-modules

### 编译命令

    $ cd uadk_engine.git/
    $ ls
    $ git status
    $ autoreconf -i
    $ ./configure
    $ make
    
### 安装

    $ sudo make install

这一步有可能出现安装路径是`/usr/local/lib`的情况。为了让 OpenSSL 3.0 能正确找到 UADK Proivder (uadk_provider.so)，需要手动把 `uadk_provider.*` 移动到 `/usr/local/lib/ossl-modules` 目录下。

    $ sudo mv /usr/local/lib/uadk_procider.* /usr/local/lib/ossl-modules

### 测试验证

检查一，确认 openssl 加载 uadk_provider 能够成功。

    $ openssl list -provider uadk_provider -all-algorithms | grep uadk
        ...
        { 2.16.840.1.101.3.4.1.21, AES-192-ECB } @ uadk_provider
        { 2.16.840.1.101.3.4.1.41, AES-256-ECB } @ uadk_provider
        { 1.2.156.10197.1.104.1, SM4-ECB } @ uadk_provider
        { 1.2.156.10197.1.104.2, SM4, SM4-CBC } @ uadk_provider
        { 1.2.156.10197.1.104.7, SM4-CTR } @ uadk_provider
        ...

检查二，确认 BiShengJDK 的 libj2kae.so 能够找到正确的 libcrypto.so.3。

        $ ldd ${JAVA_HOME}/lib/aarch64/libj2kae.so
            linux-vdso.so.1 (0x0000ffffb91a2000)
            libssl.so.3 => /usr/local/lib/libssl.so.3 (0x0000ffffb9050000)
            libcrypto.so.3 => /usr/local/lib/libcrypto.so.3 (0x0000ffffb8be0000)
            libc.so.6 => /usr/lib64/libc.so.6 (0x0000ffffb89e0000)
            /lib/ld-linux-aarch64.so.1 (0x0000ffffb9165000)

这里重点检查 `libssl.so.3` 和 `libcrypto.so.3` 的路径在 `/usr/local/lib` 之下。

检查三，使用 `openssl` 调用 `uadk_provider` 进行加解密计算。

    openssl speed -provider uadk_provider -provider default -async_jobs 1 -evp sm4-cbc
    openssl speed -decrypt -provider uadk_provider -evp sm4-cbc -bytes 1024 -seconds 1

在执行这些操作之前和之后，查看加速器硬件寄存器 `QM_DFX_DB_CNT` 值的是否有变化，来判断 UADK 确实被使用。

    sudo cat /sys/kernel/debug/hisi_sec2/*/qm/regs | grep QM_DFX_DB_CNT