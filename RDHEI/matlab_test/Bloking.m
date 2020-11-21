function [BLK,n_row,n_col] = Bloking(IMG,s)
n = (size(IMG,1)*size(IMG,2))/(s*s);
n_row = size(IMG,1)/s;
n_col = size(IMG,2)/s;
BLK = zeros(s,s,n);
k=1;
for i=1:n_col
        for j=1:n_row
            BLK(:,:,k)= IMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1));
            BLK(:,:,k) = BLK(:,:,k).'; %RASTER SCAN
            k = k+1;            
        end
end
BLK = reshape(BLK,4,n);
end