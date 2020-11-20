function [EIMG] = Encrypted(SRC,K)
    IMG = SRC(:,:,1); %SINGLE TUNNEL
    subplot(2,2,1);imshow(IMG);title("single-channel grayscale");
    subplot(2,2,2);imhist(IMG);title("it's histogram");
    %STEP1---IMG BLOCKING
    s = 2;
    n = (size(IMG,1)*size(IMG,2))/(s*s);%num of blocks
    IMG_BLK = zeros(2,2,n);
    n_row = size(IMG,1)/s;
    n_col = size(IMG,2)/s;
    k = 1;
    %需考虑IMG长度不是s的整数
    for i=1:n_col
        for j=1:n_row
            IMG_BLK(:,:,k)= IMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1));
            IMG_BLK(:,:,k) = IMG_BLK(:,:,k).'; %RASTER SCAN
            %imshow(uint8(IMG_BLK(:,:,k)));
            k = k+1;            
        end
    end
    IMG_BLK = reshape(IMG_BLK,4,n);
%produce a hash sequence
    HImg = DataHash(IMG);
    HK = DataHash(K);
    Ke = (bitxor(uint8(HImg),uint8(HK)));
%turn Ke to 256*1
    Ke256 = zeros(1,256);
    for i = 1:32
        Ke256(1,1+8*(i-1):8+8*(i-1)) = bitget(Ke(i),1:8);      
    end
%TSS
    X = zeros(n+1,1);U = zeros(2,1);
    R = zeros(n,1);V = zeros(2,1);
    %u1 = 0;u2 = 0;v1 = 0;v2 = 0;
    for i = 1:64
       U(1) = U(1)+Ke256(i)*2^(64-i); 
    end
    for i = 64:128
       U(2) = U(2)+Ke256(i)*2^(128-i); 
    end
    for i = 129:192
       V(1) = V(1)+Ke256(i)*2^(192-i); 
    end
    for i= 193:256
       V(2) = V(2)+Ke256(i)*2^(256-i);
    end
    x0 = U(1)/(2^90);%initial value x0
    r0 = U(2)/(2^90);%parameter
    
    X(1) = x0;R(1) = r0;
    for i = 2:3
        X(i) = mod(((X(i-1)*U(i-1)*V(i-1))/(2^80)+X(i-1)),1);
        R(i) = mod(((R(i-1)*U(i-1)*V(i-1))/(2^80)+R(i-1)),4);
    end
    r = 4-R(3); %r<- 4-r2,R(3) = r2;
    X(1) = X(3); %X(1) = x0,x0<-x2, X(3) = x2;
    
    %recursion of X(i),R(i) (start from X(1) not x0)
    for i = 1:n
       if(X(i)<0.5)
          X(i+1) = mod((r*X(i)/2+((4-r)*sin(pi*X(i)))/4),1);
       else
           X(i+1) = mod((r*(1-X(i))/2+((4-r)*sin(pi*X(i)))/4),1);
       end
       R(i) = floor(mod((X(i+1)*2^40),256));
    end
    
    %blocks and pixesl modulation
    R4 = [R';R';R';R'];
    %E_IMG = zeros(s*s,n);
    E_IMG = mod((IMG_BLK+R4),256);
    E_IMG = reshape(E_IMG,[2,2,n]);
%    for i = 1:n
 %      E_IMG(:,:,i) =  E_IMG(:,:,i)';
  %  end
    k = 1;
    for i=1:n_col
        for j=1:n_row
            E_IMG(:,:,k) = E_IMG(:,:,k)';
            EIMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1)) = E_IMG(:,:,k);
            %IMG_BLK(:,:,k)= IMG(1+(i-1)*s:1+(i-1)*s+(s-1),1+(j-1)*s:1+(j-1)*s+(s-1));
            %IMG_BLK(:,:,k) = IMG_BLK(:,:,k).'; %RASTER SCAN
            k = k+1;
        end
    end
    EIMG = uint8(EIMG);
    imshow(EIMG);
    Frame = getframe;
    imwrite(Frame.cdata,'e.jpg'); %这样保存会失真
    subplot(2,2,3);imshow(EIMG);title("after encypted");
    subplot(2,2,4);imhist(EIMG);title("encypted histogram");
end