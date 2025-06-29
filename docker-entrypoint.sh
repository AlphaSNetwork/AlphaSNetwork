#!/bin/bash

set -e

# Alpha区块链节点Docker入口点脚本

# 默认配置
DEFAULT_CHAIN="local"
DEFAULT_BASE_PATH="/data"
DEFAULT_LOG_LEVEL="info"
DEFAULT_RPC_PORT="9944"
DEFAULT_WS_PORT="9945"
DEFAULT_P2P_PORT="30333"

# 解析命令行参数
CHAIN=${CHAIN:-$DEFAULT_CHAIN}
BASE_PATH=${BASE_PATH:-$DEFAULT_BASE_PATH}
LOG_LEVEL=${LOG_LEVEL:-$DEFAULT_LOG_LEVEL}
RPC_PORT=${RPC_PORT:-$DEFAULT_RPC_PORT}
WS_PORT=${WS_PORT:-$DEFAULT_WS_PORT}
P2P_PORT=${P2P_PORT:-$DEFAULT_P2P_PORT}

# 节点类型
NODE_TYPE=${NODE_TYPE:-"full"}
NODE_NAME=${NODE_NAME:-"alpha-node"}

# 创建必要的目录
mkdir -p $BASE_PATH
mkdir -p /logs

# 生成链规范（如果不存在）
if [ ! -f "/alpha/chain-spec.json" ]; then
    echo "生成链规范..."
    /alpha/target/release/alpha-node build-spec --disable-default-bootnode --chain $CHAIN > /alpha/chain-spec-plain.json
    /alpha/target/release/alpha-node build-spec --chain /alpha/chain-spec-plain.json --raw --disable-default-bootnode > /alpha/chain-spec.json
fi

# 构建节点命令
NODE_CMD="/alpha/target/release/alpha-node"
NODE_ARGS=(
    "--base-path" "$BASE_PATH"
    "--chain" "/alpha/chain-spec.json"
    "--port" "$P2P_PORT"
    "--rpc-port" "$RPC_PORT"
    "--ws-port" "$WS_PORT"
    "--name" "$NODE_NAME"
    "--log" "$LOG_LEVEL"
    "--rpc-external"
    "--ws-external"
    "--rpc-cors" "all"
)

# 根据节点类型添加特定参数
case $NODE_TYPE in
    "validator")
        NODE_ARGS+=("--validator")
        NODE_ARGS+=("--rpc-methods" "Unsafe")
        echo "启动验证者节点: $NODE_NAME"
        ;;
    "full")
        NODE_ARGS+=("--rpc-methods" "Safe")
        echo "启动全节点: $NODE_NAME"
        ;;
    "archive")
        NODE_ARGS+=("--pruning" "archive")
        NODE_ARGS+=("--rpc-methods" "Safe")
        echo "启动归档节点: $NODE_NAME"
        ;;
    *)
        echo "未知节点类型: $NODE_TYPE"
        exit 1
        ;;
esac

# 添加引导节点（如果指定）
if [ ! -z "$BOOTNODES" ]; then
    NODE_ARGS+=("--bootnodes" "$BOOTNODES")
fi

# 添加遥测端点（如果指定）
if [ ! -z "$TELEMETRY_URL" ]; then
    NODE_ARGS+=("--telemetry-url" "$TELEMETRY_URL")
fi

# 处理特殊命令
case "$1" in
    "--help"|"help")
        echo "Alpha区块链节点Docker容器"
        echo ""
        echo "环境变量:"
        echo "  CHAIN          链类型 (默认: local)"
        echo "  NODE_TYPE      节点类型: validator|full|archive (默认: full)"
        echo "  NODE_NAME      节点名称 (默认: alpha-node)"
        echo "  BASE_PATH      数据目录 (默认: /data)"
        echo "  LOG_LEVEL      日志级别 (默认: info)"
        echo "  RPC_PORT       RPC端口 (默认: 9944)"
        echo "  WS_PORT        WebSocket端口 (默认: 9945)"
        echo "  P2P_PORT       P2P端口 (默认: 30333)"
        echo "  BOOTNODES      引导节点列表"
        echo "  TELEMETRY_URL  遥测端点"
        echo ""
        echo "示例:"
        echo "  docker run -e NODE_TYPE=validator alpha-node"
        echo "  docker run -e NODE_TYPE=full -p 9944:9944 alpha-node"
        exit 0
        ;;
    "key")
        # 密钥管理命令
        shift
        exec /alpha/target/release/alpha-node key "$@"
        ;;
    "build-spec")
        # 构建链规范命令
        shift
        exec /alpha/target/release/alpha-node build-spec "$@"
        ;;
    "export-blocks")
        # 导出区块命令
        shift
        exec /alpha/target/release/alpha-node export-blocks "$@"
        ;;
    "import-blocks")
        # 导入区块命令
        shift
        exec /alpha/target/release/alpha-node import-blocks "$@"
        ;;
    "purge-chain")
        # 清理链数据命令
        shift
        exec /alpha/target/release/alpha-node purge-chain "$@"
        ;;
    "benchmark")
        # 基准测试命令
        shift
        exec /alpha/target/release/alpha-node benchmark "$@"
        ;;
    *)
        # 如果有额外参数，添加到节点命令中
        if [ $# -gt 0 ]; then
            NODE_ARGS+=("$@")
        fi
        ;;
esac

# 显示启动信息
echo "========================================="
echo "Alpha区块链节点启动"
echo "========================================="
echo "节点类型: $NODE_TYPE"
echo "节点名称: $NODE_NAME"
echo "链类型: $CHAIN"
echo "数据目录: $BASE_PATH"
echo "RPC端口: $RPC_PORT"
echo "WebSocket端口: $WS_PORT"
echo "P2P端口: $P2P_PORT"
echo "日志级别: $LOG_LEVEL"
echo "========================================="

# 启动节点
exec "$NODE_CMD" "${NODE_ARGS[@]}"

