function [IMG] = UnBloking(BLK,n_row,n_col)
s = size(BLK,1)^0.5;
n = size(BLK,2);
k=1;
BLK = reshape(BLK,[2,2,n]);
for i=1:n_col
    for j=1:n_row
        BLK(:,:,k) = BLK(:,:,k)';
        IMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1)) = BLK(:,:,k);
        k = k+1;
    end
end
end