#!/bin/bash

# Alpha区块链网络部署脚本
# 版本: 1.0.0
# 作者: Alpha Team

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
NETWORK_NAME="alpha-network"
CHAIN_SPEC="genesis.json"
BASE_PATH="./data"
NODE_KEY_PATH="./keys"
LOG_LEVEL="info"
RPC_PORT=9944
WS_PORT=9945
P2P_PORT=30333

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 检查Rust
    if ! command -v rustc &> /dev/null; then
        log_error "Rust未安装，请先安装Rust"
        exit 1
    fi
    
    # 检查Substrate
    if [ ! -f "./target/release/alpha-node" ]; then
        log_warning "Alpha节点未编译，开始编译..."
        compile_node
    fi
    
    log_success "依赖检查完成"
}

# 编译节点
compile_node() {
    log_info "编译Alpha节点..."
    
    # 设置Rust环境
    source $HOME/.cargo/env
    
    # 编译节点
    cargo build --release
    
    if [ $? -eq 0 ]; then
        log_success "节点编译完成"
    else
        log_error "节点编译失败"
        exit 1
    fi
}

# 生成节点密钥
generate_keys() {
    log_info "生成节点密钥..."
    
    mkdir -p $NODE_KEY_PATH
    
    # 生成验证者密钥
    ./target/release/alpha-node key generate --scheme Sr25519 --password-interactive > $NODE_KEY_PATH/validator1.key
    ./target/release/alpha-node key generate --scheme Sr25519 --password-interactive > $NODE_KEY_PATH/validator2.key
    ./target/release/alpha-node key generate --scheme Sr25519 --password-interactive > $NODE_KEY_PATH/validator3.key
    
    # 生成会话密钥
    ./target/release/alpha-node key generate --scheme Ed25519 --password-interactive > $NODE_KEY_PATH/session1.key
    ./target/release/alpha-node key generate --scheme Ed25519 --password-interactive > $NODE_KEY_PATH/session2.key
    ./target/release/alpha-node key generate --scheme Ed25519 --password-interactive > $NODE_KEY_PATH/session3.key
    
    log_success "密钥生成完成"
}

# 初始化网络
init_network() {
    log_info "初始化Alpha网络..."
    
    # 创建数据目录
    mkdir -p $BASE_PATH
    
    # 生成链规范
    ./target/release/alpha-node build-spec --disable-default-bootnode --chain local > chain-spec-plain.json
    ./target/release/alpha-node build-spec --chain chain-spec-plain.json --raw --disable-default-bootnode > chain-spec.json
    
    # 清理旧数据
    rm -rf $BASE_PATH/*
    
    log_success "网络初始化完成"
}

# 启动验证者节点
start_validator() {
    local node_id=$1
    local port_offset=$((node_id * 10))
    local rpc_port=$((RPC_PORT + port_offset))
    local ws_port=$((WS_PORT + port_offset))
    local p2p_port=$((P2P_PORT + port_offset))
    
    log_info "启动验证者节点 $node_id..."
    
    ./target/release/alpha-node \
        --base-path $BASE_PATH/validator$node_id \
        --chain chain-spec.json \
        --port $p2p_port \
        --rpc-port $rpc_port \
        --ws-port $ws_port \
        --validator \
        --rpc-methods Unsafe \
        --name "Alpha-Validator-$node_id" \
        --telemetry-url "wss://telemetry.polkadot.io/submit/ 0" \
        --log $LOG_LEVEL \
        > logs/validator$node_id.log 2>&1 &
    
    echo $! > $BASE_PATH/validator$node_id.pid
    
    log_success "验证者节点 $node_id 已启动 (PID: $(cat $BASE_PATH/validator$node_id.pid))"
}

# 启动全节点
start_full_node() {
    local node_id=$1
    local port_offset=$((node_id * 10 + 100))
    local rpc_port=$((RPC_PORT + port_offset))
    local ws_port=$((WS_PORT + port_offset))
    local p2p_port=$((P2P_PORT + port_offset))
    
    log_info "启动全节点 $node_id..."
    
    ./target/release/alpha-node \
        --base-path $BASE_PATH/full$node_id \
        --chain chain-spec.json \
        --port $p2p_port \
        --rpc-port $rpc_port \
        --ws-port $ws_port \
        --rpc-methods Safe \
        --name "Alpha-Full-$node_id" \
        --telemetry-url "wss://telemetry.polkadot.io/submit/ 0" \
        --log $LOG_LEVEL \
        > logs/full$node_id.log 2>&1 &
    
    echo $! > $BASE_PATH/full$node_id.pid
    
    log_success "全节点 $node_id 已启动 (PID: $(cat $BASE_PATH/full$node_id.pid))"
}

# 停止所有节点
stop_network() {
    log_info "停止Alpha网络..."
    
    # 停止验证者节点
    for i in {1..3}; do
        if [ -f "$BASE_PATH/validator$i.pid" ]; then
            local pid=$(cat $BASE_PATH/validator$i.pid)
            if kill -0 $pid 2>/dev/null; then
                kill $pid
                log_info "验证者节点 $i 已停止"
            fi
            rm -f $BASE_PATH/validator$i.pid
        fi
    done
    
    # 停止全节点
    for i in {1..2}; do
        if [ -f "$BASE_PATH/full$i.pid" ]; then
            local pid=$(cat $BASE_PATH/full$i.pid)
            if kill -0 $pid 2>/dev/null; then
                kill $pid
                log_info "全节点 $i 已停止"
            fi
            rm -f $BASE_PATH/full$i.pid
        fi
    done
    
    log_success "网络已停止"
}

# 检查网络状态
check_status() {
    log_info "检查网络状态..."
    
    echo "验证者节点状态:"
    for i in {1..3}; do
        if [ -f "$BASE_PATH/validator$i.pid" ]; then
            local pid=$(cat $BASE_PATH/validator$i.pid)
            if kill -0 $pid 2>/dev/null; then
                echo "  验证者节点 $i: 运行中 (PID: $pid)"
            else
                echo "  验证者节点 $i: 已停止"
            fi
        else
            echo "  验证者节点 $i: 未启动"
        fi
    done
    
    echo "全节点状态:"
    for i in {1..2}; do
        if [ -f "$BASE_PATH/full$i.pid" ]; then
            local pid=$(cat $BASE_PATH/full$i.pid)
            if kill -0 $pid 2>/dev/null; then
                echo "  全节点 $i: 运行中 (PID: $pid)"
            else
                echo "  全节点 $i: 已停止"
            fi
        else
            echo "  全节点 $i: 未启动"
        fi
    done
}

# 清理网络数据
clean_network() {
    log_warning "清理网络数据..."
    
    # 停止所有节点
    stop_network
    
    # 删除数据目录
    rm -rf $BASE_PATH
    rm -rf logs
    rm -f chain-spec*.json
    
    log_success "网络数据已清理"
}

# 部署测试网络
deploy_testnet() {
    log_info "部署Alpha测试网络..."
    
    # 创建日志目录
    mkdir -p logs
    
    # 检查依赖
    check_dependencies
    
    # 初始化网络
    init_network
    
    # 启动验证者节点
    start_validator 1
    sleep 5
    start_validator 2
    sleep 5
    start_validator 3
    sleep 5
    
    # 启动全节点
    start_full_node 1
    sleep 3
    start_full_node 2
    
    log_success "Alpha测试网络部署完成!"
    log_info "RPC端点: http://localhost:9944"
    log_info "WebSocket端点: ws://localhost:9945"
    log_info "使用 './deploy.sh status' 检查网络状态"
}

# 部署主网
deploy_mainnet() {
    log_warning "部署Alpha主网..."
    log_warning "这将启动生产环境的区块链网络"
    
    read -p "确认要部署主网吗? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        log_info "主网部署已取消"
        exit 0
    fi
    
    # 使用主网配置
    CHAIN_SPEC="genesis.json"
    
    deploy_testnet
    
    log_success "Alpha主网部署完成!"
}

# 显示帮助信息
show_help() {
    echo "Alpha区块链网络部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  testnet    部署测试网络"
    echo "  mainnet    部署主网"
    echo "  stop       停止网络"
    echo "  status     检查网络状态"
    echo "  clean      清理网络数据"
    echo "  keys       生成节点密钥"
    echo "  compile    编译节点"
    echo "  help       显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 testnet    # 部署测试网络"
    echo "  $0 status     # 检查网络状态"
    echo "  $0 stop       # 停止网络"
}

# 主函数
main() {
    case "${1:-help}" in
        "testnet")
            deploy_testnet
            ;;
        "mainnet")
            deploy_mainnet
            ;;
        "stop")
            stop_network
            ;;
        "status")
            check_status
            ;;
        "clean")
            clean_network
            ;;
        "keys")
            generate_keys
            ;;
        "compile")
            compile_node
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"

