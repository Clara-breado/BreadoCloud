function [OIMG] = Recovery(EIMG,Ke)
s = 2;
n = (size(EIMG,1)*size(EIMG,2))/(s*s);
%blocking
[E_IMG,n_row,n_col] = Bloking(EIMG,s);
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
    
    O_IMG = mod((E_IMG-R4),256);
    
    OIMG = UnBloking(O_IMG,n_row,n_col);
    OIMG = uint8(OIMG);
    imshow(OIMG);

end