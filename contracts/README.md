# EchoPrime Contracts

On-chain oracle registry for the [EchoPrime](https://github.com/DarrenEdwards111/EchoPrime) project — a public, immutable record of verified safe primes and their Collapse Scores.

## What It Does

The **EchoPrimeOracle** smart contract stores verified safe prime submissions on Ethereum. Authorized oracle bots submit safe primes along with their Collapse Scores (see [whitepaper](../docs/whitepaper.md)), and anyone can query the registry.

Key features:

- **Immutable registry** — once a prime is submitted, it can never be altered
- **Authorized submitters** — only approved oracle bots can write records
- **Batch submissions** — submit up to 100 primes in a single transaction
- **Fully on-chain** — all data stored in contract storage, queryable by anyone

## Quick Start

```bash
# Install dependencies
npm install

# Compile the contract
npx hardhat compile

# Run tests
npx hardhat test

# Deploy to local Hardhat node
npx hardhat node                            # Terminal 1
npx hardhat run scripts/deploy.js --network localhost  # Terminal 2

# Submit demo primes (set CONTRACT_ADDRESS in .env first)
npx hardhat run scripts/submit-prime.js --network localhost
```

## Contract API

### Write Functions (authorized only)

| Function | Description |
| --- | --- |
| `submitVerification(index, p, scoreP, scoreQ, verified)` | Submit a single safe prime |
| `batchSubmit(indices[], primes[], scoresP[], scoresQ[], verifieds[])` | Submit up to 100 primes |

### Read Functions (public)

| Function | Returns |
| --- | --- |
| `getPrime(index)` | Full `PrimeRecord` struct |
| `isPrimeSubmitted(index)` | `bool` |
| `getSubmittedIndices()` | `uint256[]` of all submitted indices |
| `totalSubmissions()` | Total count |
| `records(index)` | Direct mapping access |

### Admin Functions (owner only)

| Function | Description |
| --- | --- |
| `addSubmitter(address)` | Authorize an oracle bot |
| `removeSubmitter(address)` | Revoke authorization |
| `transferOwnership(address)` | Transfer contract ownership |

### PrimeRecord Struct

```solidity
struct PrimeRecord {
    uint256 p;          // Safe prime
    uint256 q;          // Sophie Germain prime (p-1)/2
    uint256 scoreP;     // Collapse score for p (scaled 1e18)
    uint256 scoreQ;     // Collapse score for q (scaled 1e18)
    bool verified;      // Primality test passed
    address submitter;  // Oracle bot address
    uint256 timestamp;  // Block timestamp
}
```

## Deployment (Sepolia)

1. Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

2. Deploy:

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

3. Verify on Etherscan:

```bash
npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
```

## Environment Variables

| Variable | Description |
| --- | --- |
| `SEPOLIA_RPC_URL` | Sepolia RPC endpoint (default: `https://rpc.sepolia.org`) |
| `PRIVATE_KEY` | Deployer wallet private key |
| `ETHERSCAN_API_KEY` | For contract verification |
| `CONTRACT_ADDRESS` | Deployed contract address (for scripts) |

## Project Links

- **SDK:** [`echoprime-sdk`](https://www.npmjs.com/package/echoprime-sdk)
- **Whitepaper:** [`docs/whitepaper.md`](../docs/whitepaper.md)
- **Repository:** [github.com/DarrenEdwards111/EchoPrime](https://github.com/DarrenEdwards111/EchoPrime)

## Project Structure

```
contracts/
├── src/
│   ├── EchoPrimeOracle.sol      # Main oracle contract
│   └── IEchoPrimeOracle.sol     # Interface
├── scripts/
│   ├── deploy.js                # Hardhat deploy script
│   └── submit-prime.js          # Submit demo primes
├── test/
│   └── EchoPrimeOracle.test.js  # 20 contract tests
├── hardhat.config.js
├── package.json
└── README.md
```

## License

Apache-2.0 — © 2025 Mikoshi Ltd
