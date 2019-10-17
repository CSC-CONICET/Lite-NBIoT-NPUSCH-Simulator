function e = nbiotLteRateMatchTurbo(coded,E,Qm,iRV)
% nbiotLteRateMatchTurbo  TS 36.212 5.1.4
%   nbiotLteRateMatchTurbo(coded,E,Qm,iRV)
%
%   coded is a one dimentional array with 3 turbo encoded parity streams
%   concatenated block-wise to form the encoded output i.e. [S P1 P2]
%   where S is the systematic bits, P1 is the encoder 1 bits and P2 is the
%   encoder 2 bits.
%
%   E is the target output size
%
%   Qm is de Modulation order, 1 For BPSK, 2 For QPSK
%
%   iRV is the redundancy version index. 0 or 2 for N

%% Sub Block Interleaver

    %Constantes       
    PP= [ 0, 16, 8, 24, 4, 20, 12, 28, 2, 18, 10, 26, 6, 22, 14, 30, ...
        1,17, 9, 25, 5, 21, 13, 29, 3, 19, 11, 27, 7, 23, 15, 31 ]; %permutation pattern    
    
    D=numel(coded)/3; %stream size : TBS + 24 CRC + 4 Turbo Tail
    d=reshape(coded,[],3)'; % [systemic ; parity 1 ; parity2]
    
    Csubblock=32; %Columnas de la matriz de permutacion
    Rsubblock=ceil(D/Csubblock);
               
    %NOTE: Uso -1 en TC para marcar los bits nulos
    padding=-ones(1,Csubblock*Rsubblock-D);
    
    %Systemic
    Y1=[padding d(1,:) ]; 
    TC=reshape(Y1,[Csubblock,Rsubblock])'; %Permutation Matrix    
    v(1,:)=reshape(TC(:,PP+1),[Csubblock*Rsubblock,1])';
    
    %Parity 1
    Y2=[padding d(2,:) ];
    TC=reshape(Y2,[Csubblock,Rsubblock])'; %Permutation Matrix    
    v(2,:)=reshape(TC(:,PP+1),[Csubblock*Rsubblock,1])';
    
    %Parity 2
    Y3=[padding d(3,:) ];
    k=[0:numel(Y3)-1]; %Indices para la funcion
    v(3,:)=Y3(mod(PP(floor(k/Rsubblock)+1)+32*mod(k,Rsubblock)+1,Rsubblock*Csubblock)+1);
    
    %% Bit collection
    w=[v(1,:) reshape(v([2 3],:),1,[])];
    
    %% Bit Selection and pruning              
    Ncb=numel(w); % Ncb = Kw
    k0=Rsubblock*(2*ceil(Ncb/8/Rsubblock)*iRV+2); % Ncb = Kw = numel(2)
    
    e=-ones(E,1); %creo buffer de salida
    
    j=0; k=0;
    while k < E
        l=mod(k0 + j,Ncb);
        if w(l+1) ~= -1 
            e(k+1)=w(l+1);
            k=k+1;
        end
    j=j+1;   
    end
    
end