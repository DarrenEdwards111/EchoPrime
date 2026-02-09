// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @title EchoPrimeOracle
 * @notice Public on-chain registry for verified safe prime submissions.
 *         Authorized oracle bots submit safe primes along with their
 *         Collapse Scores. Anyone can query the registry.
 * @dev    Scores are scaled by 1e18 (fixed-point), so 1.0 == 1e18.
 */
contract EchoPrimeOracle {
    struct PrimeRecord {
        uint256 p;          // Safe prime
        uint256 q;          // Sophie Germain prime (p-1)/2
        uint256 scoreP;     // Collapse score for p (scaled by 1e18, so 1.0 = 1e18)
        uint256 scoreQ;     // Collapse score for q (scaled by 1e18)
        bool verified;      // Whether both p and q passed primality testing
        address submitter;  // Who submitted this
        uint256 timestamp;  // When it was submitted
    }

    // Owner (deployer) - can add/remove authorized submitters
    address public owner;

    // Authorized submitters (oracle bots)
    mapping(address => bool) public authorizedSubmitters;

    // Prime registry: index => PrimeRecord
    mapping(uint256 => PrimeRecord) public records;

    // Track which indices have been submitted
    uint256 public totalSubmissions;
    uint256[] public submittedIndices;

    // Events
    event PrimeVerified(
        uint256 indexed index,
        uint256 p,
        uint256 q,
        uint256 scoreP,
        uint256 scoreQ,
        bool verified,
        address indexed submitter
    );

    event SubmitterAdded(address indexed submitter);
    event SubmitterRemoved(address indexed submitter);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyAuthorized() {
        require(authorizedSubmitters[msg.sender] || msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedSubmitters[msg.sender] = true;
    }

    /**
     * @notice Submit a verified safe prime record.
     * @param index  Unique index for this prime in the registry.
     * @param p      The safe prime (must be odd and > 2).
     * @param scoreP Collapse score for p (scaled 1e18).
     * @param scoreQ Collapse score for q (scaled 1e18).
     * @param verified Whether primality testing passed for both p and q.
     */
    function submitVerification(
        uint256 index,
        uint256 p,
        uint256 scoreP,
        uint256 scoreQ,
        bool verified
    ) external onlyAuthorized {
        require(records[index].p == 0, "Index already submitted");
        require(p > 2, "Invalid prime");
        require(p % 2 == 1, "Prime must be odd");

        uint256 q = (p - 1) / 2;

        records[index] = PrimeRecord({
            p: p,
            q: q,
            scoreP: scoreP,
            scoreQ: scoreQ,
            verified: verified,
            submitter: msg.sender,
            timestamp: block.timestamp
        });

        submittedIndices.push(index);
        totalSubmissions++;

        emit PrimeVerified(index, p, q, scoreP, scoreQ, verified, msg.sender);
    }

    /**
     * @notice Batch-submit multiple verified safe primes.
     * @dev    Silently skips indices that have already been submitted.
     *         Maximum 100 entries per call.
     */
    function batchSubmit(
        uint256[] calldata indices,
        uint256[] calldata primes,
        uint256[] calldata scoresP,
        uint256[] calldata scoresQ,
        bool[] calldata verifieds
    ) external onlyAuthorized {
        require(indices.length == primes.length, "Length mismatch");
        require(indices.length == scoresP.length, "Length mismatch");
        require(indices.length == scoresQ.length, "Length mismatch");
        require(indices.length == verifieds.length, "Length mismatch");
        require(indices.length <= 100, "Batch too large");

        for (uint256 i = 0; i < indices.length; i++) {
            if (records[indices[i]].p != 0) continue; // Skip already submitted

            uint256 q = (primes[i] - 1) / 2;

            records[indices[i]] = PrimeRecord({
                p: primes[i],
                q: q,
                scoreP: scoresP[i],
                scoreQ: scoresQ[i],
                verified: verifieds[i],
                submitter: msg.sender,
                timestamp: block.timestamp
            });

            submittedIndices.push(indices[i]);
            totalSubmissions++;

            emit PrimeVerified(indices[i], primes[i], q, scoresP[i], scoresQ[i], verifieds[i], msg.sender);
        }
    }

    // ── Query functions ────────────────────────────────────────────────

    function getPrime(uint256 index) external view returns (PrimeRecord memory) {
        return records[index];
    }

    function isPrimeSubmitted(uint256 index) external view returns (bool) {
        return records[index].p != 0;
    }

    function getSubmittedIndices() external view returns (uint256[] memory) {
        return submittedIndices;
    }

    // ── Admin functions ────────────────────────────────────────────────

    function addSubmitter(address submitter) external onlyOwner {
        authorizedSubmitters[submitter] = true;
        emit SubmitterAdded(submitter);
    }

    function removeSubmitter(address submitter) external onlyOwner {
        authorizedSubmitters[submitter] = false;
        emit SubmitterRemoved(submitter);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }
}
