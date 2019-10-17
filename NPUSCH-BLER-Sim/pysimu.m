function  retvals = pysimu(IMCS,IRU,IREP,ISNR,MONO)        
        IMCS=double(IMCS);
        IRU=double(IRU);
        IREP=double(IREP);
        ISNR=double(ISNR);
        MONO=logical(MONO);

        numTrBlks = 2^15;                % Number of simulated
        %numTrBlks = 2^20;                % Number of simulated

        %SNR = -35+ISNR*0.5;  %-35 to 25
        SNR = -30+ISNR*0.1;  %-35 to 25
        
        enb.NNCellID = 0;              % NB-IoT physical cell ID
        enb.CyclicPrefixUL = 'Normal'; % NB-IoT only support normal cyclic prefix
        enb.CellRefP = 1;              % Number of NRS antenna ports, should be either 1 or 2
        enb.NFrame = 0;                % Frame number to start with the simulation
        enb.NSubframe = 0;             % Subframe number to start with the simulation   
        
        npuschInfo = hNPUSCHInfo;        
        npuschInfo.IMCS = IMCS;
        npuschInfo.IRU = IRU;
        npuschInfo.MONO = MONO;
        
%         if npuschInfo.TBS ~= 256
%             continue
%         end
                    
        NPUSCH.TrBlkSize = npuschInfo.TBS;                             % Transport block size
        NPUSCH.IMCS=npuschInfo.IMCS;
        %Bits Per RU

        if (MONO)
            NULSLOTS=16;
        else
            NULSLOTS=24;
        end
        
        NULSYMBSLOT=6; %7simbolos por slot, pero uno se usa para DMRS

        %TODO: Revisar esto.
        G = NULSLOTS*NULSYMBSLOT*npuschInfo.Qm;                        % Number of available bits per RU
        NPUSCH.CodedTrBlkSize = npuschInfo.NRU*G;                      % Coded transport block size

        NPUSCH.NRU = npuschInfo.NRU;        
        NPUSCH.IRU = npuschInfo.IRU;        
        
        NPUSCH.Qm = npuschInfo.Qm;

        %NPUSCH.NRUPerNPDSCH = npuschInfo.NREP*npuschInfo.NRU;
        %NPUSCH.NSubframesPerNPDSCH = npdschInfo.NREP*npdschInfo.NSF; % The number of subframes for a NPDSCH when considering repetitions

        
        %%
        % Verify the configured higher layer parameters using the DLSCH code rate.
        % The code rate is the ratio between the number of bits after CRC coding
        % and the number of bits after rate matching. For the case when |SIB1NB| is
        % set to |true|, the code rate |R| can be larger than or equal to 1, which
        % is not a valid scenario. For example, such case happens when |ISF| is set
        % to 0 and |SchedulingInfoSIB1| is set to 3.

        R = (NPUSCH.TrBlkSize+24)/NPUSCH.CodedTrBlkSize;  % DLSCH channel coding rate, 24 denotes the number of CRC bits
        if R >= 1
            error(['ULSCH coding rate larger than or equal to 1 for the configured higher layer parameters. NRU = ' ...
                num2str(NPUSCH.NRU) '; TBS = ' num2str(NPUSCH.TrBlkSize) '; Coded block size = ' num2str(NPUSCH.CodedTrBlkSize) ...
                '; Modulation Order = ' num2str(NPUSCH.Qm) '; Rate = ' num2str(R)]);
        end


        %%
        % Configure the following NPDSCH parameters:
        %
        % * Modulation scheme.
        % * The radio network temporary identifier (RNTI) for NPDSCH scrambling
        % sequence initialization.
        % * The transmission scheme according to the number of NRS antenna ports.
        % * The number of transmission layers according to the number of NRS
        % antenna ports.

        switch NPUSCH.Qm
            case 1
                NPUSCH.Modulation = 'BPSK'; 
            case 2
                NPUSCH.Modulation = 'QPSK'; 
            otherwise
                error(['Modulation Order Qm=' num2str(NPUSCH.Qm) 'Not Supported']);
        end            


        NPUSCH.RNTI = 1; %  radio network temporary identifier

        % RNTI
        % if enb.CellRefP == 1
        %     NPDSCH.TxScheme = 'Port0';          % Transmission scheme
        %     NPDSCH.NLayers = 1;                 % Number of layers 
        % elseif enb.CellRefP == 2
        %     NPDSCH.TxScheme = 'TxDiversity';
        %     NPDSCH.NLayers = 2;                             
        % else
        %     error('Number of antenna ports is not correct, should be either 1 or 2');
        % end

        %NSubframe = enb.NFrame*10+enb.NSubframe;                   % Absolute subframe number at the starting point of the simulation
        %TotSubframes = NPUSCH.NSubframesPerNPUSCH*numTrBlks;       % Calculate total number of subframes to simulate

        %bler = zeros(1,numel(SNR));                                % Initialize BLER result     
                
                    
            npuschInfo.IREP = IREP;
            NPUSCH.NREP = npuschInfo.NREP;
            NPUSCH.IREP = npuschInfo.IREP;
            
            
            
            
            [rIMCS rIRU rIREP rSNR rbler] = runSimulation(NPUSCH, SNR, enb, numTrBlks );
            
            retvals.IMCS  = IMCS;
            retvals.IRU   = IRU;
            retvals.IREP  = IREP;        
            retvals.ISNR  = ISNR;
            retvals.snr   = SNR;
            retvals.bler  = rbler;
            retvals.tbs   = int64(npuschInfo.TBS);
            retvals.totru = int64(npuschInfo.NREP  * npuschInfo.NRU);
            
end
