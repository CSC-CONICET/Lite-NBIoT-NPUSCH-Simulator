A=csvread('lala.csv');
G=A;
%G=A( A(:,5)>0 & A(:,5)<1,:);

npuschInfo = hNPUSCHInfo;
for row = 1:size(G,1)
npuschInfo.IMCS = G(row,1);
npuschInfo.IRU = G(row,2);
npuschInfo.IREP = G(row,3);
G(row,6)=npuschInfo.TBS;
G(row,7)= npuschInfo.NREP  * npuschInfo.NRU;
end

csvwrite('badout.csv',G)

%         if npuschInfo.TBS ~= 256