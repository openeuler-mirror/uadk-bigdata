# 介绍 BiSheng JDK 的调试开发和部署测试

- [介绍 BiSheng JDK 的调试开发和部署测试](#介绍-bisheng-jdk-的调试开发和部署测试)
  - [BiSheng JDK 8.0 源代码下载](#bisheng-jdk-80-源代码下载)
- [在 openEuler 23.03 的 docker container 中编译](#在-openeuler-2303-的-docker-container-中编译)
  - [一些 `KAE Provider` 测试命令](#一些-kae-provider-测试命令)
- [在 Ubuntu 2204 的 docker container 中编译](#在-ubuntu-2204-的-docker-container-中编译)
  - [创建 docker container](#创建-docker-container)
  - [鉴于缺少 Boot JDK](#鉴于缺少-boot-jdk)
  - [准备工作 JTReg](#准备工作-jtreg)
  - [现在可以编译 JDK](#现在可以编译-jdk)
  - [编译结果`JRE`位于](#编译结果jre位于)
  - [如何使用编译出来的 JDK / JRE ？](#如何使用编译出来的-jdk--jre-)
  - [关于 `make test TEST=jdk_kae_security`](#关于-make-test-testjdk_kae_security)
- [参考，涉及的主要文件](#参考涉及的主要文件)
- [libj2kae.so (Native JNI)](#libj2kaeso-native-jni)
  - [相关的测试命令：](#相关的测试命令)
  - [Linking libj2kae.so](#linking-libj2kaeso)
- [调试方法](#调试方法)
  - [单独方式来运行SM4Test](#单独方式来运行sm4test)
  - [可能有用的 JDK 编译 Configure 配置项](#可能有用的-jdk-编译-configure-配置项)

## BiSheng JDK 8.0 源代码下载

本项目参考两个源。具体区别后面会讲到。官方源是BiSheng JDK团队的正式发布源。要使用硬件加速器的 SM4 算法，请使用“ KAEProvider 适配 OpenSSL 3.0 之私有源”。

1. 官方源：https://gitee.com/openeuler/bishengjdk-8.git (tag: jdk8u402-ga-b011)。

1. KAEProvider 适配 OpenSSL 3.0 之私有源： https://gitee.com/docularxu/bishengjdk-8.git (branch: [working-jdk8u402-kaeprovider-ossl3.0](https://gitee.com/docularxu/bishengjdk-8/commits/working-jdk8u402-kaeprovider-ossl3.0))。

本项目的操作使用的物理机是鲲鹏920。Docker containter 基于 OpenEuler 23.03 和 Ubuntu 22.04 两种。

关于编译和测试，主要参考[Building the JDK by OpenJDK](https://openjdk.org/groups/build/doc/building.html)。

# 在 openEuler 23.03 的 docker container 中编译

从[这里](https://github.com/docularxu/build-containers)获得编译需要的 Dockerfile。运行`docker build`命令构建所需的 docker container。可以参考代码仓中的`README.md`

    docker build -t jdk-dev:openeuler.2303 - < Dockerfile.oeuler.2303.jdk-dev
    docker run -it -v /home/guodong/working:/mnt jdk-dev:openeuler.2303 /bin/bash


## 一些 `KAE Provider` 测试命令

 (来源：Bisheng JDK 8.0 Wiki 之 [KAE Provider用户使用手册](https://gitee.com/openeuler/bishengjdk-8/wikis/%E4%B8%AD%E6%96%87%E6%96%87%E6%A1%A3/KAE%20Provider%E7%94%A8%E6%88%B7%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C))

    $ java -Djava.security.debug=kae -Dkae.conf=/home/user/kaeprovider.conf ProviderTest
    $ java -Djava.security.debug=kae -Dkae.log=true -Dkae.log.file=/home/user/logs/kae.log ProviderTest
    $ java -Dkae.log=true -Dkae.log.file=/home/xiezhaokun/logs/kae.log -Dkae.engine.id=uadk_engine -Dkae.libcrypto.useGlobalMode=true   ProviderTest

# 在 Ubuntu 2204 的 docker container 中编译

因为 UADK, UADK Provider 3.0, OpenSSL 3.0 都是在基于 Ubuntu 2204 的 docker container 中完成的。在与 BishengJDK 1.8.0 集成时，需要把 BishengJDK 编译也放到 Ubuntu 2204 环境中，这样才能让 KAEProvider 和 UADK Provider + OpenSSL 3.0 都在用一个 container 容器中。

从[这里](https://github.com/docularxu/build-containers)获得编译需要的 Dockerfile。下面的步骤是基于这个 Dockerfile 的：`Dockerfile.ubuntu.2204.uadk-dev`。

## 创建 docker container

这里介绍用于 BishengJDK-1.8.0 编译的 docker container 的创建。

参考 [README.md](https://github.com/docularxu/build-containers) 创建 docker image。

    docker build -f Dockerfile.ubuntu.2204.uadk-dev . -t uadk-jdk-dev:ubuntu.2204

基于此 docker image，使用所提供的脚本[`docker-run-uadk-dev.sh`](https://github.com/docularxu/build-containers) 创建 container。

    docker-run-uadk-dev.sh ubuntu-jdk-uadk <give_it_a_name>

## 鉴于缺少 Boot JDK

在aarch64平台，下载 bisheng-jdk 官方编译版本

    sudo apt-get install -y wget
    wget --no-check-certificate  https://mirrors.huaweicloud.com/kunpeng/archive/compiler/bisheng_jdk/bisheng-jdk-8u402-linux-aarch64.tar.gz
    tar zxf bisheng-jdk-8u402-linux-aarch64.tar.gz

如此，解压后的目录，就可以做为接下来编译 JDK 的命令行参数`--with-boot-jdk=解压路径/bisheng-jdk1.8.0_402`

## 准备工作 JTReg

JTReg 是 JDK 的测试框架之一，被用于大部分测试用例。按照OpenJDK官方 [building 文档](https://openjdk.org/groups/build/doc/building.html)，从[这里下载 jtreg 5.1](https://ci.adoptium.net/view/Dependencies/job/dependency_pipeline/lastSuccessfulBuild/artifact/jtreg/)。（Note：The Adoption Group provides recent builds of jtreg here. Download the latest `.tar.gz` file, unpack it, and point `--with-jtreg` to the jtreg directory that you just unpacked.）

## 现在可以编译 JDK

    unset JAVA_HOME
    make dist-clean   // optional

    bash ./configure --enable-kae \
            --with-extra-cflags='-Wno-error=nonnull' \
            --with-jtreg=/home/guodong/jtreg \
            --with-boot-jdk=/home/guodong/bisheng-jdk1.8.0_402

Note: /usr/share/jtreg: exists in ubuntu 22.04. It can be used too.

    make all JOBS=128

or, 打印更多的 build log，可以使用 `LOG=`

    make all LOG=debug

编译 log 保存在：The output (stdout and stderr) from the latest build is always stored in:

    $BUILD=./build/linux-aarch64-normal-server-release
    $BUILD/build.log.

## 编译结果`JRE`位于

`j2sdk` is for development: it has everything you need to build Java applications. j2sdk Image (Java 2 Software Development Kit)。
`j2re` is for execution: it runs compiled Java applications. j2re Image (Java 2 Runtime Environment)。

    j2re-image: $BUILD/images/j2re-image
    j2sdk-image: $BUILD/images/j2sdk-image 

注意：In later versions of OpenJDK (starting around JDK 9), the naming conventions were simplified to `jdk` and `jre` for better clarity. The core functionality remains the same.

## 如何使用编译出来的 JDK / JRE ？

通过设置环境变量`JAVA_HOME`指向编译出的 j2sdk-image 目录，就可以使用。

    export JAVA_HOME=./build/linux-aarch64-normal-server-release/images/j2sdk-image

系统通常把 JDK 安装在 `/usr/lib/jvm/` 目录中。
TODO: 举例

    sudo cp -rf [bishengjdk-8.git]/build/linux-aarch64-normal-server-release/images/j2sdk-image /opt/bisheng_jdk8u382-ga-b011-ossl1.1.1f
    export JAVA_HOME=/opt/bisheng_jdk8u382-ga-b011-ossl1.1.1f
    export PATH=$JAVA_HOME/bin:$PATH
    which java
        (验证，这里应该返回 /opt/bisheng_jdk8u382-ga-b011-ossl1.1.1f/bin/java )

## 关于 `make test TEST=jdk_kae_security`

测试结果，从 `.jtr` 文件查看。

    vi build/linux-aarch64-normal-server-release/testoutput/jdk_kae_security/JTwork/org/openeuler/security/openssl/SM4Test.jtr
    vi build/linux-aarch64-normal-server-release/testoutput/jdk_kae_security/JTwork/org/openeuler/security/openssl/KAELogTest.jtr
    vi build/linux-aarch64-normal-server-release/testoutput/jdk_kae_security/JTwork/org/openeuler/security/openssl/KAEDebugLogTest.jtr

# 参考，涉及的主要文件

1. Java secruity 引擎选择

    ${JAVA_HOME}/lib/security/java.security

1. KAEProvider 相关文件分布

    1. CONF 配置文件：
        1. kaeprovider.conf
            jdk/src/share/lib/security/kaeprovider.conf
        2. openssl-loadbalancing.cnf
            jdk/src/share/lib/security/openssl-loadbalancing.cnf

    1. C 文件（Native Library, JNI, libj2kae.so）：
        jdk/src/solaris/native/org/openeuler/security/openssl/*.c
    1. Java 文件（KAEProvider，Class）：
        jdk/src/solaris/classes/org/openeuler/security/openssl/*.java
    1. Make 文件
        1. jdk/make/lib/SecurityLibraries.gmk
        2. jdk/make/CopyFiles.gmk
    1. Test 文件：
        1. jdk_kae_security 测试集：jdk/test/TEST.groups: jdk_kae_security = org/openeuler/security/openssl
        1. Java 测试用例: jdk/test/org/openeuler/security/openssl/*.java (eg. ProviderTest.java, SM4Test.java)

    1. 测试结果 `.jtr`：

        build/linux-aarch64-normal-server-release/testoutput/jdk_kae_security/JTwork/org/openeuler/security/openssl/SM4Test.jtr

    1. KAEProvider 编译结果, Native JNI, `libj2kae.so`:

        build/linux-aarch64-normal-server-release/images/j2sdk-image/jre/lib/aarch64/libj2kae.so

    1. java.security 配置文件，通过修改`jre/lib/security/java.security`文件，添加 KAE Provider，并设置其优先级。举例，设置 KAE Provider 为最高优先级:

        security.provider.1=org.openeuler.security.openssl.KAEProvider
        security.provider.2=sun.security.provider.Sun

# libj2kae.so (Native JNI)

## 相关的测试命令：

    $ readelf -d ./build/linux-aarch64-normal-server-release/jdk/lib/aarch64/libj2kae.so | grep '(RPATH)' -A2
        0x000000000000000f (RPATH)              Library rpath: [$ORIGIN]


## Linking libj2kae.so

libj2kae.so 是 KAEProvider 的 Native JNI 库，由这些文件构成，以及  -ldl -ldl -lssl -lcrypto
链接构成。

对应的 C 文件在目录：jdk/src/solaris/native/org/openeuler/security/openssl/*.c

需要注意它所链接的 libcrypto.so, libssl.so 是哪个版本？

    $ ldd ./build/linux-aarch64-normal-server-release/images/j2sdk-image/jre/lib/aarch64/libj2kae.so
            linux-vdso.so.1 (0x0000ffff8c2c8000)
            libssl.so.3 => /usr/local/lib/libssl.so.3 (0x0000ffff8c110000)
            libcrypto.so.3 => /usr/local/lib/libcrypto.so.3 (0x0000ffff8bbd0000)
            libc.so.6 => /lib/aarch64-linux-gnu/libc.so.6 (0x0000ffff8ba20000)
            /lib/ld-linux-aarch64.so.1 (0x0000ffff8c28f000)

在 uadk-dev container 中，OpenSSL 3.0 的确安装在 /usr/local/lib 下面。可以通过 `ldd /usr/local/bin/openssl` 获得验证。

# 调试方法

## 单独方式来运行SM4Test

    make 
    make test TEST=jdk_kae_security 
    jtreg -verbose:all \
            -jdk:/home/guodong/bishengjdk-8.git/build/linux-aarch64-normal-server-release/images/j2sdk-image \
            /home/guodong/bishengjdk-8.git/jdk/test/org/openeuler/security/openssl/SM4Test.java

    build/linux-aarch64-normal-server-release/images/j2sdk-image/bin/java \
    -classpath /home/guodong/bishengjdk-8.git/JTwork/classes/org/openeuler/security/openssl \
    SM4Test

## 可能有用的 JDK 编译 Configure 配置项

Certain third-party libraries used by the JDK (libjpeg, giflib, libpng, lcms and zlib) are included in the JDK repository. The default behavior of the JDK build is to use the included ("bundled") versions of libjpeg, giflib, libpng and lcms. For zlib, the system lib (if present) is used except on Windows and AIX. However the bundled libraries may be replaced by an external version. 

    --with-zlib=<source> - Use the specified source for zlib