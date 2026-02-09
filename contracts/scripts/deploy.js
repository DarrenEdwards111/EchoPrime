const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying EchoPrimeOracle with account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

  const EchoPrimeOracle = await hre.ethers.getContractFactory("EchoPrimeOracle");
  const oracle = await EchoPrimeOracle.deploy();
  await oracle.waitForDeployment();

  const address = await oracle.getAddress();
  console.log("EchoPrimeOracle deployed to:", address);
  console.log("");
  console.log("Add this to your .env file:");
  console.log(`CONTRACT_ADDRESS=${address}`);
  console.log("");
  console.log("To verify on Etherscan:");
  console.log(`npx hardhat verify --network sepolia ${address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
