function [n_payload,MIMG] = Marked(EIMG,SD)
subplot(2,2,1);imshow(EIMG);title("before embedded");
subplot(2,2,2);imhist(EIMG);title("histogram");
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
[IMG_BLK,n_row,n_col] = Bloking(EIMG,s);
IMG_BLK = uint8(IMG_BLK);
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
            PN = [PN,bitget(A,1),bitget(A,2)];
            A = bitset(A,1,0);
            A = bitset(A,2,0);
        case 1
           A = IMG_BLK(PE_INDEX(i));
           A = bitset(A,1,1);
           A = bitset(A,2,0); 
        case 2
            A = IMG_BLK(PE_INDEX(i));
            A = bitset(A,1,0);
            A = bitset(A,2,1);
        case 3
            A = IMG_BLK(PE_INDEX(i));
            A = bitset(A,1,1);
            A = bitset(A,2,1);
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

PE_INDEX = find(PN_FLAG==1|PN_FLAG==2|PN_FLAG==3);
PAYLOAD = [uint2bit(PS),PN,uint2bit(SD)];n_payload = size(PAYLOAD,2);

nstr_payload = num2str(n_payload);n_nstr = size(nstr_payload,2);% '78951'---5 ;first 8 bit to store this
nbit_payload = uint2bit(uint8(nstr_payload));
PAYLOAD = [uint2bit(n_nstr),nbit_payload,PAYLOAD];%add header for PAYLOAD

%PAYLOAD = [PAYLOAD,ones(1,(size(PE_INDEX,1)*6-n_payload))];%init

k = 1;
for i=1:size(PE_INDEX)
    A = IMG_BLK(PE_INDEX(i));
    %modified PE remain bits(8-alpha)
    for j = 3:8
        if(k>size(PAYLOAD,2))
            break
        end        
        A = bitset(A,j,PAYLOAD(k));
        k = k+1;
    end
    IMG_BLK(PE_INDEX(i)) = A;
end
MIMG = UnBloking(IMG_BLK,n_row,n_col);
subplot(2,2,3);imshow(MIMG);title("after embedded");
subplot(2,2,4);imhist(MIMG);title("histogram");
%figure;imshow(MIMG);
end