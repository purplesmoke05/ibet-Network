
pragma solidity ^0.8.0;

error InsufficientBalance(uint256 available, uint256 required, string msg);

library ErrorCode {
    string constant ERR_001 ="ERR_001";
    string constant ERR_101 ="ERR_101";
    string constant ERR_201 ="ERR_201";
    string constant ERR_301 ="ERR_301";
    string constant ERR_401 ="ERR_401";
    string constant ERR_501 ="ERR_501";
}

