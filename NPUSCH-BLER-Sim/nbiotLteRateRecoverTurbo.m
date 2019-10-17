function softCoded = nbiotLteRateRecoverTurbo(IN,TBS,Qm,iRV)
%   nbiotLteRateMatchTurbo(coded,E,Qm,iRV)
%
%   IN is a one dimentional array, output of LteRateMatchTurbo.
%
%   TBS is the transmission block size, before appling CRC and turbo
%   encoding
%
%   Qm is de Modulation order, 1 For BPSK, 2 For QPSK
%
%   iRV is the redundancy version index. 0 or 2 for NBIOT

    
%% Reverse Bit selection and prunning
%First find prunned positions by rateMatching placeholded vector


    %Permutation Pattern
    PP = [ 0, 16, 8, 24, 4, 20, 12, 28, 2, 18, 10, 26, 6, 22, 14, 30, ...
         1,17, 9, 25, 5, 21, 13, 29, 3, 19, 11, 27, 7, 23, 15, 31 ];
        
    D = TBS+24+4;%stream size : TBS + 24 CRC + 4 Turbo Tail
    
    %NOTE: Soft Decoding
    % In(i)= 0  : Bit Null
    % IN(i)> 0  : Bit 0
    % IN(i)< 0  : Bit 1
    
    softCoded=zeros(D*3,1); %Placeholder soft coded stream
    
    d=reshape(softCoded,[],3)'; % [systemic ; parity 1 ; parity2]
    
    Csubblock=32; %Columnas de la matriz de permutacion
    Rsubblock=ceil(D/Csubblock);
    
    
    %NOTE: Uso nan en TC para marcar los bits nulos
    padding=nan*ones(1,Csubblock*Rsubblock-D);
    
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
    
    % Bit collection
    w=[v(1,:) reshape(v([2 3],:),1,[])];                     
    Ncb=numel(w); % Ncb = Kw
    
    % Reverse bit selection
    k0=Rsubblock*(2*ceil(Ncb/8/Rsubblock)*iRV+2);
    E=numel(IN);
    e=IN;
    
    j=0; k=0;
    while k < E
        l=mod(k0 + j,Ncb);
        if ~ isnan(w(l+1)) 
           w(l+1) = w(l+1)+e(k+1); %Soft combine if same bit is encoded twice.
           k=k+1;
        end
    j=j+1;   
    end   
    
    %% Reverse Bit collection
    V=Rsubblock*Csubblock;
    v=[w(1:V) ; w(V+[1:2:2*V]); w(V+1+[1:2:2*V])];
    
    %% Reverse Interleaver
    
    %Systemic    
    TC=reshape(v(1,:),Rsubblock,Csubblock);
    Y1=reshape(TC(:,PP+1)',1,Csubblock*Rsubblock);
    d(1,:)=Y1(Csubblock*Rsubblock-D+1:end);
    
    %Parity 1
    TC=reshape(v(2,:),Rsubblock,Csubblock);
    Y2=reshape(TC(:,PP+1)',1,Csubblock*Rsubblock);    
    d(2,:)=Y2(Csubblock*Rsubblock-D+1:end);
    
    %Parity 2
    k=[0:V-1]; %Indices para la funcion
    [~,idx] = sort(mod(PP(floor(k/Rsubblock)+1)+32*mod(k,Rsubblock)+1,Rsubblock*Csubblock));
    Y3=v(3,idx);
    d(3,:)= Y3(Csubblock*Rsubblock-D+1:end);
    
    
    softCoded = reshape(d',[],1);
end