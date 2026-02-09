const hre = require("hardhat");

// Known safe primes for demo submission
// A safe prime p satisfies: p is prime AND q = (p-1)/2 is also prime
const SAFE_PRIMES = [
  { index: 1, p: 5n },    // q = 2
  { index: 2, p: 7n },    // q = 3
  { index: 3, p: 11n },   // q = 5
  { index: 4, p: 23n },   // q = 11
  { index: 5, p: 47n },   // q = 23
];

// Simple collapse score placeholder (scaled by 1e18)
function collapseScore(n) {
  // Placeholder: score = 1 / ln(n), scaled by 1e18
  const score = 1.0 / Math.log(Number(n));
  return BigInt(Math.floor(score * 1e18));
}

async function main() {
  const contractAddress = process.env.CONTRACT_ADDRESS;
  if (!contractAddress) {
    console.error("Set CONTRACT_ADDRESS in .env first (run deploy.js)");
    process.exit(1);
  }

  const [signer] = await hre.ethers.getSigners();
  console.log("Submitting primes with account:", signer.address);

  const oracle = await hre.ethers.getContractAt("EchoPrimeOracle", contractAddress, signer);

  for (const { index, p } of SAFE_PRIMES) {
    const q = (p - 1n) / 2n;
    const scoreP = collapseScore(p);
    const scoreQ = collapseScore(q);

    // Check if already submitted
    const existing = await oracle.isPrimeSubmitted(index);
    if (existing) {
      console.log(`Index ${index} already submitted, skipping`);
      continue;
    }

    console.log(`Submitting index=${index}  p=${p}  q=${q}  scoreP=${scoreP}  scoreQ=${scoreQ}`);
    const tx = await oracle.submitVerification(index, p, scoreP, scoreQ, true);
    await tx.wait();
    console.log(`  ✓ tx: ${tx.hash}`);
  }

  // Read back and verify
  console.log("\n── Registry Contents ──");
  const total = await oracle.totalSubmissions();
  console.log(`Total submissions: ${total}`);

  for (const { index } of SAFE_PRIMES) {
    const rec = await oracle.getPrime(index);
    console.log(`  [${index}] p=${rec.p} q=${rec.q} scoreP=${rec.scoreP} scoreQ=${rec.scoreQ} verified=${rec.verified}`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
