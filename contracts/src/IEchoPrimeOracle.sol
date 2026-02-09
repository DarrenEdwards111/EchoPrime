// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @title IEchoPrimeOracle
 * @notice Interface for the EchoPrime on-chain oracle registry.
 */
interface IEchoPrimeOracle {
    struct PrimeRecord {
        uint256 p;
        uint256 q;
        uint256 scoreP;
        uint256 scoreQ;
        bool verified;
        address submitter;
        uint256 timestamp;
    }

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

    // Write
    function submitVerification(
        uint256 index,
        uint256 p,
        uint256 scoreP,
        uint256 scoreQ,
        bool verified
    ) external;

    function batchSubmit(
        uint256[] calldata indices,
        uint256[] calldata primes,
        uint256[] calldata scoresP,
        uint256[] calldata scoresQ,
        bool[] calldata verifieds
    ) external;

    // Read
    function owner() external view returns (address);
    function authorizedSubmitters(address) external view returns (bool);
    function totalSubmissions() external view returns (uint256);
    function getPrime(uint256 index) external view returns (PrimeRecord memory);
    function isPrimeSubmitted(uint256 index) external view returns (bool);
    function getSubmittedIndices() external view returns (uint256[] memory);

    // Admin
    function addSubmitter(address submitter) external;
    function removeSubmitter(address submitter) external;
    function transferOwnership(address newOwner) external;
}
