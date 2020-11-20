SRC = imread('G:\gradethree\RDHEI\src.jpg');
%假设取通道1
%IMG = SRC(:,:,3);
IMG = EIMG;
figure;imshow(IMG);
s=2;n = (size(IMG,1)*size(IMG,2))/(s*s);
n_row = size(IMG,1)/s;
n_col = size(IMG,2)/s;
k=1;
for i=1:n_col
        for j=1:n_row
            IMG_BLK(:,:,k)= IMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1));
            IMG_BLK(:,:,k) = IMG_BLK(:,:,k).'; %RASTER SCAN
            %imshow(uint8(IMG_BLK(:,:,k)));
            k = k+1;            
        end
end
IMG_BLK = reshape(IMG_BLK,4,n);

k=1;
IMG_BLK = reshape(IMG_BLK,[2,2,n]);
for i=1:n_col
        for j=1:n_row
            IMG_BLK(:,:,k) = IMG_BLK(:,:,k)';
            EIMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1)) = IMG_BLK(:,:,k);
            k = k+1;
        end
end
figure;imshow(EIMG);
