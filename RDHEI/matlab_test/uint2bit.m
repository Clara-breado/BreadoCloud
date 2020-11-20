function[bitform] = uint2bit(Uint)
bitform = 0;
for j = 1:size(Uint,2)
    for i = 1:8
       bitform = [bitform,bitget(Uint(j),i)] ;
    end
end
bitform = uint8(bitform(2:size(bitform,2)));%DELETE THE FIRST ELEMENT    
end