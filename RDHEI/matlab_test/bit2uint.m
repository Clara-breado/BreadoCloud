function[Uint] = bit2uint(bitform)
n_Uint = ceil(size(bitform,2)/8);
Uint = zeros(1,n_Uint);%init
k =1;
for i = 1:n_Uint
    tmp = 0;
   for j = 1:8
       if(k<=size(bitform,2))
           tmp = tmp+bitform(k)*(2^(j-1));
           k = k+1;
       end
   end
   Uint(i) = tmp;
end
Uint = uint8(Uint);

end