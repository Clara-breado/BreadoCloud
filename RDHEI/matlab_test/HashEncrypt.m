function [HashData] = HashEncrypt(data,K)
    Hdata = DataHash(data);
    HK = DataHash(K);
    HashData = (bitxor(uint8(Hdata),uint8(HK)));
end