SRC = imread('G:\gradethree\RDHEI\src.jpg');
alpha = 2;beta = 2;
%须随机取一个通道作为隐藏层--->3通道转1通道
R = SRC(:,:,1);
G = SRC(:,:,2);
B = SRC(:,:,3);
%假设取通道1
IMG = SRC(:,:,3);
figure;imshow(IMG)
%STEP1---IMG BLOCKING
s = 2;
n = (size(IMG,1)*size(IMG,2))/(s*s);
%IMG_BLK = reshape(IMG,2,2,n);
IMG_BLK = zeros(2,2,n);
E = zeros(2,2,n);
n_row = size(IMG,1)/s;
n_col = size(IMG,2)/s;
k = 1;
%需考虑IMG长度不是s的整数
for i=1:n_row
    for j=1:n_col
        IMG_BLK(:,:,k)= IMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1));
        IMG_BLK(:,:,k) = IMG_BLK(:,:,k).';
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

IMG_BLK_BIT = uint8(IMG_BLK);
%PN_INDEX = find(PN_FLAG==0);
PE_INDEX = find(PN_FLAG~=-1);%pe---->1 2 3

%todo: use alpha & beta to sustitute
for i=1:size(PE_INDEX)
    tmp = PN_FLAG(PE_INDEX(i));
    switch(tmp)
        case 0
            A = IMG_BLK(PE_INDEX(i));
            A = bitset(A,8,0);
            A = bitset(A,7,0);
        case 1
           A = IMG_BLK(PE_INDEX(i));
           A = bitset(A,8,0);
           A = bitset(A,7,1); 
        case 2
            A = IMG_BLK(PE_INDEX(i));
            A = bitset(A,8,1);
            A = bitset(A,7,0);
        case 3
            A = IMG_BLK(PE_INDEX(i));
            A = bitset(A,8,1);
            A = bitset(A,7,1);
    end
    IMG_BLK(PE_INDEX(i)) = A;%return
    
end
n_PN = size(find(PN_FLAG==0),1);
n_PE = size(find(PN_FLAG==1),1)+size(find(PN_FLAG==2),1)+size(find(PN_FLAG==3),1);
n_payload = (8-alpha)*n_PE-beta*n_PN-8;
%figure;imshow(IMG_BLK);
%二叉树分类G1 G2