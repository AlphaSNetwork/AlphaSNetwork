# Alpha区块链节点Docker镜像
FROM ubuntu:22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV RUST_BACKTRACE=1
ENV RUST_LOG=info

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    clang \
    libssl-dev \
    llvm \
    libudev-dev \
    make \
    protobuf-compiler \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 设置工作目录
WORKDIR /alpha

# 复制源代码
COPY . .

# 编译Alpha节点
RUN source /root/.cargo/env && cargo build --release

# 创建数据目录
RUN mkdir -p /data /keys /logs

# 暴露端口
EXPOSE 9944 9945 30333

# 设置入口点
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["--help"]

