function [n_payload] = Marked(EIMG,SD)
%parameter 
alpha = 2;beta = 2;
%EIMG for encrypted img,SD for secret data
SD = uint8(SD);%ch --> uint8
%STEP1---IMG BLOCKING
s = 2;
n = (size(EIMG,1)*size(EIMG,2))/(s*s);
%IMG_BLK = reshape(IMG,2,2,n);
%IMG_BLK = zeros(2,2,n);
E = zeros(2,2,n);
n_row = size(EIMG,1)/s;
n_col = size(EIMG,2)/s;
%需考虑IMG长度不是s的整数
figure;imshow(EIMG);
k = 1;
for i=1:n_col
        for j=1:n_row
            IMG_BLK(:,:,k)= EIMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1));
            IMG_BLK(:,:,k) = IMG_BLK(:,:,k).'; %RASTER SCAN
            %imshow(uint8(IMG_BLK(:,:,k)));
            k = k+1;            
        end
end
IMG_BLK = reshape(IMG_BLK,4,n);

%STEP2--grouping
PR = IMG_BLK(1,:);
PS = IMG_BLK(2,1);
p_err = 1;%(nalpha-1)/2
PN_FLAG = zeros(s*s,n);%PN_FLAG==1,PN;PNFLAG==0,PE
PN_FLAG(1,:) = -1;%PR
PN_FLAG(2,1) = -1;%PS
    %calculate E
    PR4 = zeros(2,2,n);
    for i=1:n
        for j = 2:4
       %PR4(:,:,i) = PR(:,:,i)*ones;
       %E(:,:,i) = abs(IMG_BLK(:,:,i)-PR4(:,:,i));
       e = (PR(1,i)-IMG_BLK(j,i));
       if((e>p_err)||(e<-1*p_err))
           PN_FLAG(j,i)=0;
       elseif(e == -1)
           PN_FLAG(j,i)=1;
       elseif(e == 0)
           PN_FLAG(j,i)=2;
       elseif(e == 1)
           PN_FLAG(j,i)=3;
       end
       
        end
    end
%STEP3--Pixel labeling using PBTL

%IMG_BLK_BIT = uint8(IMG_BLK);
%PN_INDEX = find(PN_FLAG==0);
PE_INDEX = find(PN_FLAG~=-1);%pe---->1 2 3

%todo: use alpha & beta to sustitute
PN = zeros(1,1);

for i=1:size(PE_INDEX)
    tmp = PN_FLAG(PE_INDEX(i));
    switch(tmp)
        case 0 %PN 
            A = IMG_BLK(PE_INDEX(i));
            PN = [PN,bitget(A,7),bitget(A,8)];
            A = bitset(A,7,0);
            A = bitset(A,8,0);
        case 1
           A = IMG_BLK(PE_INDEX(i));
           A = bitset(A,7,0);
           A = bitset(A,8,1); 
        case 2
            A = IMG_BLK(PE_INDEX(i));
            A = bitset(A,7,1);
            A = bitset(A,8,0);
        case 3
            A = IMG_BLK(PE_INDEX(i));
            A = bitset(A,7,1);
            A = bitset(A,8,1);
    end
    IMG_BLK(PE_INDEX(i)) = A;%return    
end

%STEP4---payload embedding
% the original 8 bits of pixel in Ps, the replaced original β bits of each pixel in Pn, and the secret data.
n_PN = size(find(PN_FLAG==0),1);
n_PE = size(find(PN_FLAG==1),1)+size(find(PN_FLAG==2),1)+size(find(PN_FLAG==3),1);
n_payload = (8-2)*n_PE-2*n_PN-8;%SD<n_payload
PN = uint8(PN(2:size(PN,2)));%DELETE THE FIRST ELEMENT
%PS = uint2bit(PS);

PAYLOAD = [uint2bit(PS),PN,uint2bit(SD)];


PE_INDEX = find(PN_FLAG==1|PN_FLAG==2|PN_FLAG==3);

k = 1;
for i=1:size(PE_INDEX)
    %modified PE remain bits(8-alpha)
    for j = 1:6
        if(k>size(PAYLOAD,2))
            break
        end
        A = IMG_BLK(PE_INDEX(i));
        A = bitset(A,j,PAYLOAD(k));
        k = k+1;
    end
    IMG_BLK(PE_INDEX(i)) = A;
end

IMG_BLK = reshape(IMG_BLK,[2,2,n]);
k = 1;
for i=1:n_col
    for j=1:n_row
        IMG_BLK(:,:,k) = IMG_BLK(:,:,k)';
        MIMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1)) = IMG_BLK(:,:,k);
        k = k+1;
    end
end
figure;imshow(MIMG);
end