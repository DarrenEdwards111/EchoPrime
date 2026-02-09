const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("EchoPrimeOracle", function () {
  let oracle;
  let owner, addr1, addr2;

  const SCORE_1E18 = ethers.parseEther("1"); // 1e18

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("EchoPrimeOracle");
    oracle = await Factory.deploy();
    await oracle.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should deploy correctly", async function () {
      expect(await oracle.getAddress()).to.be.properAddress;
    });

    it("Owner should be deployer", async function () {
      expect(await oracle.owner()).to.equal(owner.address);
    });

    it("Deployer should be an authorized submitter", async function () {
      expect(await oracle.authorizedSubmitters(owner.address)).to.be.true;
    });

    it("Should start with zero submissions", async function () {
      expect(await oracle.totalSubmissions()).to.equal(0);
    });
  });

  describe("Submit Verification", function () {
    it("Should submit a prime and emit event", async function () {
      const p = 5n;
      const q = 2n; // (5-1)/2

      await expect(
        oracle.submitVerification(1, p, SCORE_1E18, SCORE_1E18, true)
      )
        .to.emit(oracle, "PrimeVerified")
        .withArgs(1, p, q, SCORE_1E18, SCORE_1E18, true, owner.address);

      expect(await oracle.totalSubmissions()).to.equal(1);
    });

    it("Should reject duplicate index", async function () {
      await oracle.submitVerification(1, 5, SCORE_1E18, SCORE_1E18, true);

      await expect(
        oracle.submitVerification(1, 7, SCORE_1E18, SCORE_1E18, true)
      ).to.be.revertedWith("Index already submitted");
    });

    it("Should reject unauthorized submitter", async function () {
      await expect(
        oracle.connect(addr1).submitVerification(1, 5, SCORE_1E18, SCORE_1E18, true)
      ).to.be.revertedWith("Not authorized");
    });

    it("Should reject even numbers", async function () {
      await expect(
        oracle.submitVerification(1, 4, SCORE_1E18, SCORE_1E18, true)
      ).to.be.revertedWith("Prime must be odd");
    });

    it("Should reject zero and small values", async function () {
      await expect(
        oracle.submitVerification(1, 0, SCORE_1E18, SCORE_1E18, true)
      ).to.be.revertedWith("Invalid prime");

      await expect(
        oracle.submitVerification(1, 1, SCORE_1E18, SCORE_1E18, true)
      ).to.be.revertedWith("Invalid prime");

      await expect(
        oracle.submitVerification(1, 2, SCORE_1E18, SCORE_1E18, true)
      ).to.be.revertedWith("Invalid prime");
    });
  });

  describe("Batch Submit", function () {
    it("Should batch submit primes", async function () {
      const indices = [1, 2, 3];
      const primes = [5, 7, 11];
      const scoresP = [SCORE_1E18, SCORE_1E18, SCORE_1E18];
      const scoresQ = [SCORE_1E18, SCORE_1E18, SCORE_1E18];
      const verifieds = [true, true, true];

      await oracle.batchSubmit(indices, primes, scoresP, scoresQ, verifieds);

      expect(await oracle.totalSubmissions()).to.equal(3);
      expect(await oracle.isPrimeSubmitted(1)).to.be.true;
      expect(await oracle.isPrimeSubmitted(2)).to.be.true;
      expect(await oracle.isPrimeSubmitted(3)).to.be.true;
    });

    it("Should skip already submitted indices in batch", async function () {
      await oracle.submitVerification(1, 5, SCORE_1E18, SCORE_1E18, true);

      await oracle.batchSubmit([1, 2], [5, 7], [SCORE_1E18, SCORE_1E18], [SCORE_1E18, SCORE_1E18], [true, true]);

      // Total should be 2: the original + index 2 from batch (index 1 skipped)
      expect(await oracle.totalSubmissions()).to.equal(2);
    });

    it("Should reject batch with mismatched lengths", async function () {
      await expect(
        oracle.batchSubmit([1, 2], [5], [SCORE_1E18], [SCORE_1E18], [true])
      ).to.be.revertedWith("Length mismatch");
    });
  });

  describe("Query Functions", function () {
    beforeEach(async function () {
      await oracle.submitVerification(1, 5, SCORE_1E18, SCORE_1E18 / 2n, true);
      await oracle.submitVerification(2, 7, SCORE_1E18 * 2n, SCORE_1E18, false);
    });

    it("Should query primes correctly", async function () {
      const rec1 = await oracle.getPrime(1);
      expect(rec1.p).to.equal(5);
      expect(rec1.q).to.equal(2); // (5-1)/2
      expect(rec1.scoreP).to.equal(SCORE_1E18);
      expect(rec1.scoreQ).to.equal(SCORE_1E18 / 2n);
      expect(rec1.verified).to.be.true;
      expect(rec1.submitter).to.equal(owner.address);

      const rec2 = await oracle.getPrime(2);
      expect(rec2.p).to.equal(7);
      expect(rec2.q).to.equal(3); // (7-1)/2
      expect(rec2.verified).to.be.false;
    });

    it("Should report submitted indices", async function () {
      const indices = await oracle.getSubmittedIndices();
      expect(indices.length).to.equal(2);
      expect(indices[0]).to.equal(1);
      expect(indices[1]).to.equal(2);
    });

    it("Should report unsubmitted index as not submitted", async function () {
      expect(await oracle.isPrimeSubmitted(99)).to.be.false;
    });
  });

  describe("Admin Functions", function () {
    it("Should add submitters", async function () {
      expect(await oracle.authorizedSubmitters(addr1.address)).to.be.false;

      await expect(oracle.addSubmitter(addr1.address))
        .to.emit(oracle, "SubmitterAdded")
        .withArgs(addr1.address);

      expect(await oracle.authorizedSubmitters(addr1.address)).to.be.true;

      // addr1 should now be able to submit
      await oracle.connect(addr1).submitVerification(1, 5, SCORE_1E18, SCORE_1E18, true);
      expect(await oracle.totalSubmissions()).to.equal(1);
    });

    it("Should remove submitters", async function () {
      await oracle.addSubmitter(addr1.address);

      await expect(oracle.removeSubmitter(addr1.address))
        .to.emit(oracle, "SubmitterRemoved")
        .withArgs(addr1.address);

      expect(await oracle.authorizedSubmitters(addr1.address)).to.be.false;

      // addr1 should no longer be able to submit
      await expect(
        oracle.connect(addr1).submitVerification(1, 5, SCORE_1E18, SCORE_1E18, true)
      ).to.be.revertedWith("Not authorized");
    });

    it("Should transfer ownership", async function () {
      await expect(oracle.transferOwnership(addr1.address))
        .to.emit(oracle, "OwnershipTransferred")
        .withArgs(owner.address, addr1.address);

      expect(await oracle.owner()).to.equal(addr1.address);

      // Old owner can no longer add submitters
      await expect(
        oracle.addSubmitter(addr2.address)
      ).to.be.revertedWith("Not owner");

      // New owner can
      await oracle.connect(addr1).addSubmitter(addr2.address);
      expect(await oracle.authorizedSubmitters(addr2.address)).to.be.true;
    });

    it("Should reject transferring ownership to zero address", async function () {
      await expect(
        oracle.transferOwnership(ethers.ZeroAddress)
      ).to.be.revertedWith("Invalid address");
    });

    it("Non-owner cannot add submitters", async function () {
      await expect(
        oracle.connect(addr1).addSubmitter(addr2.address)
      ).to.be.revertedWith("Not owner");
    });
  });
});
