# Alpha Blockchain

Alpha Blockchain is a decentralized social network built on Substrate framework. It provides a complete Layer 1 blockchain solution for social media applications with native AlphaCoin token integration.

## Features

- **Decentralized Social Network**: Post content, like, comment, and follow users
- **Native Token (AlphaCoin)**: Earn rewards for social activities
- **IPFS Integration**: Decentralized content storage
- **Cross-platform Support**: Web, mobile, and desktop applications
- **Privacy-focused**: End-to-end encryption for private messages
- **Substrate-based**: Built on the robust Substrate framework

## Architecture

### Core Components

1. **Alpha Runtime**: The blockchain runtime containing all business logic
2. **AlphaCoin Pallet**: Native token and social features implementation
3. **Node**: The blockchain node implementation with P2P networking
4. **RPC**: JSON-RPC interface for client applications

### Key Pallets

- `pallet-alpha-coin`: Core social and token functionality
- `pallet-balances`: Account balance management
- `pallet-aura`: Block production consensus
- `pallet-grandpa`: Block finality consensus
- `pallet-sudo`: Administrative functions

## Getting Started

### Prerequisites

- Rust (latest stable)
- Git
- Build dependencies: `clang`, `libssl-dev`, `llvm`, `libudev-dev`, `protobuf-compiler`

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AlphaSNetwork/AlphaSNetwork.git
cd alpha-blockchain
```

2. Install Rust dependencies:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

3. Install system dependencies (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y git clang curl libssl-dev llvm libudev-dev make protobuf-compiler
```

4. Build the project:
```bash
cargo build --release
```

### Running the Node

#### Development Mode

Start a development node with pre-funded accounts:

```bash
./target/release/alpha-node --dev
```

#### Local Testnet

Start a local testnet with multiple validators:

```bash
# Terminal 1 - Alice
./target/release/alpha-node \
  --base-path /tmp/alice \
  --chain local \
  --alice \
  --port 30333 \
  --ws-port 9945 \
  --rpc-port 9933 \
  --node-key 0000000000000000000000000000000000000000000000000000000000000001 \
  --telemetry-url "wss://telemetry.polkadot.io/submit/ 0" \
  --validator

# Terminal 2 - Bob
./target/release/alpha-node \
  --base-path /tmp/bob \
  --chain local \
  --bob \
  --port 30334 \
  --ws-port 9946 \
  --rpc-port 9934 \
  --telemetry-url "wss://telemetry.polkadot.io/submit/ 0" \
  --validator \
  --bootnodes /ip4/127.0.0.1/tcp/30333/p2p/12D3KooWEyoppNCUx8Yx66oV9fJnriXwCcXwDDUA2kj6vnc6iDEp
```

## Social Features

### Creating Posts

Users can create social posts with content stored on IPFS:

```rust
// Create a post
alpha_coin::create_post(origin, content_hash)
```

### Liking Posts

Users can like posts from other users and earn rewards:

```rust
// Like a post
alpha_coin::like_post(origin, post_id)
```

### Following Users

Build social connections by following other users:

```rust
// Follow a user
alpha_coin::follow_user(origin, target_account)
```

### Token Rewards

- **Post Creation**: Earn AlphaCoin for creating content
- **Receiving Likes**: Earn AlphaCoin when others like your content
- **Social Engagement**: Additional rewards for active participation

## Token Economics

### AlphaCoin (ALC)

- **Symbol**: ALC
- **Decimals**: 12
- **Total Supply**: Configurable
- **Use Cases**:
  - Social activity rewards
  - Content promotion
  - Platform governance
  - Premium features

### Reward Structure

- Post creation: 100 ALC
- Receiving a like: 10 ALC
- Post deposit: 1,000 ALC (refundable)

## Development

### Project Structure

```
alpha-blockchain/
├── node/                 # Blockchain node implementation
├── runtime/              # Runtime logic and configuration
├── pallets/
│   ├── alpha-coin/      # Core social and token pallet
│   └── alpha-social/    # Additional social features (future)
├── Cargo.toml           # Workspace configuration
└── README.md
```

### Building Custom Pallets

To add new functionality, create a new pallet:

```bash
mkdir pallets/my-pallet
cd pallets/my-pallet
# Create Cargo.toml and src/lib.rs
```

### Testing

Run the test suite:

```bash
cargo test
```

Run specific pallet tests:

```bash
cargo test -p pallet-alpha-coin
```

### Benchmarking

Enable runtime benchmarks:

```bash
cargo build --release --features runtime-benchmarks
```

Run benchmarks:

```bash
./target/release/alpha-node benchmark pallet \
  --chain dev \
  --pallet pallet_alpha_coin \
  --extrinsic "*" \
  --steps 50 \
  --repeat 20
```

## Client Integration

### Polkadot.js API

Connect to the Alpha blockchain using Polkadot.js:

```javascript
import { ApiPromise, WsProvider } from '@polkadot/api';

const wsProvider = new WsProvider('ws://127.0.0.1:9944');
const api = await ApiPromise.create({ provider: wsProvider });

// Create a post
const tx = api.tx.alphaCoin.createPost(contentHash);
await tx.signAndSend(keyring.alice);
```

### Substrate Connect

For browser-based light clients:

```javascript
import { createScProvider } from '@substrate/connect';

const provider = createScProvider(chainSpec);
const api = await ApiPromise.create({ provider });
```

## Deployment

### Production Node

For production deployment:

1. Build optimized binary:
```bash
cargo build --release
```

2. Create chain specification:
```bash
./target/release/alpha-node build-spec --chain local > alpha-spec.json
```

3. Generate raw chain spec:
```bash
./target/release/alpha-node build-spec --chain alpha-spec.json --raw > alpha-spec-raw.json
```

4. Start validator node:
```bash
./target/release/alpha-node \
  --base-path /var/lib/alpha \
  --chain alpha-spec-raw.json \
  --validator \
  --name "Alpha Validator" \
  --telemetry-url "wss://telemetry.polkadot.io/submit/ 0"
```

### Docker Deployment

Build Docker image:

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY target/release/alpha-node /usr/local/bin/

EXPOSE 30333 9933 9944

ENTRYPOINT ["alpha-node"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [docs.alpha.social](https://docs.alpha.social)
- Discord: [Alpha Community](https://discord.gg/alpha)
- GitHub Issues: [Report bugs](https://github.com/AlphaSNetwork/AlphaSNetwork/issues)
## Roadmap

- [ ] Mobile SDK development
- [ ] IPFS integration
- [ ] Cross-chain bridges
- [ ] Governance implementation
- [ ] Privacy features enhancement
- [ ] Performance optimizations

