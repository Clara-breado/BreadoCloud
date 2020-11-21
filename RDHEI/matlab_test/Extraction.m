function [EIMG,ED] = Extraction(MIMG)
alpha =2;beta =2;%they should be extract from ps
p_err = 1;%it should be cal by alpha;
s=2;
n = (size(MIMG,1)*size(MIMG,2))/(s*s);
[M_IMG,n_row,n_col] = Bloking(MIMG,s);
M_IMG = uint8(M_IMG);
%grouping
PR = M_IMG(1,:);
PS = M_IMG(2,1);

PN_FLAG = zeros(s*s,n);%PN = 0; PE = 1 2 3
PN_FLAG(1,:) = -1;%PR
PN_FLAG(2,1) = -1;%PS
BIAS = zeros(s*s,n);%PE's bias
%R_bit = zeros(1,2);%replace bit
for i=1:n
    for j = 2:4
        a = M_IMG(j,i);
        R_bit = bitget(a,1)+bitget(a,2);
        switch(R_bit)
            case 0 
                PN_FLAG(j,i) = 0;
            case 1
                PN_FLAG(j,i) = 1;
                BIAS(j,i) = -1;
            case 2
                PN_FLAG(j,i) = 2;
                BIAS(j,i) = 0;
            case 3
                PN_FLAG(j,i) = 3;
                BIAS(j,i) = 1;
        end
    end
end

%extract from PE
PE_INDEX = find(PN_FLAG==1|PN_FLAG==2|PN_FLAG==3);
k = 1;
%ED_bit;%embedded data
ED_bit = 0;
for i=1:size(PE_INDEX)
    A = M_IMG(PE_INDEX(i));
    %modified PE remain bits(8-alpha)
    for j = 3:8
        ED_bit = [ED_bit,bitget(A,j)];
    end
end
ED_bit = ED_bit(2:size(ED_bit,2));
%get the length of Embedding data
n_nstr = bit2uint(ED_bit(1:8));
char_payload = bit2uint(ED_bit(9:(n_nstr+1)*8));
n_payload = 0;
for i =1:n_nstr
   n_payload = [n_payload char(char_payload(i))]; 
end
n_payload = n_payload(2:size(n_payload,2));
n_payload = str2double(n_payload);

ED_bit = ED_bit((double(n_nstr)+1)*8+1:(double(n_nstr)+1)*8+n_payload);%cut the header of PAYLOAD protocol and other
%recover PS PN
PN_INDEX = find(PN_FLAG==0);
n_pn = size(PN_INDEX,1);
for i =1:n_pn
    A = M_IMG(PN_INDEX(i));
    A = bitset(A,1,ED_bit(k));
    A = bitset(A,2,ED_bit(k+1));
    M_IMG(PN_INDEX(i)) = A;
    k = k+2;
end
%recover ED
ED_bit = ED_bit(8+2*n_pn+1:size(ED_bit,2));%foward:ps pn
%PN = ED_bit(((double(n_nstr)+1)*8+1):((double(n_nstr)+1)*8+1+n_pn*6));
ED = bit2uint(ED_bit);
char_ED = 0;
for i =1:size(ED,2)
   char_ED = [char_ED char(ED(i))]; 
end
char_ED = char_ED(2:size(char_ED,2));
ED = char_ED;
end