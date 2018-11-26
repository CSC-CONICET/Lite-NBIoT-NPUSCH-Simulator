numTrBlks = 2^15;                % Number of simulated transport blocks 
vOut=[];               
%vSNR=[-13 2 ];                  % SNR range in dB
vSNR=[2:-1:-16];

vIRU = [0:7];                       % Resource assignment field in DCI (DCI format N1 or N2)
vIREP = [0:7];                      % Repetition number field in DCI (DCI format N1 or N2)
vIMCS = [0:10];

profileName = parallel.defaultClusterProfile();
clust = parcluster(profileName);
%clust.NumWorkers = 8;
%pool = parpool(clust, 8)
job = createJob(clust);

for IMCS = vIMCS
    for IRU= vIRU

        enb.NNCellID = 0;              % NB-IoT physical cell ID
        enb.CyclicPrefixUL = 'Normal'; % NB-IoT only support normal cyclic prefix
        enb.CellRefP = 1;              % Number of NRS antenna ports, should be either 1 or 2
        enb.NFrame = 0;                % Frame number to start with the simulation
        enb.NSubframe = 0;             % Subframe number to start with the simulation   
        
        npuschInfo = hNPUSCHInfo;        
        npuschInfo.IMCS = IMCS;
        npuschInfo.IRU = IRU;
        
%         if npuschInfo.TBS ~= 256
%             continue
%         end
            
        
        NPUSCH.TrBlkSize = npuschInfo.TBS;                             % Transport block size
        NPUSCH.IMCS=npuschInfo.IMCS;
        %Bits Per RU

        NULSLOTS=16;
        NULSYMBSLOT=6; %7simbolos por slot, pero uno se usa para DMRS

        %TODO: Revisar esto.
        G = NULSLOTS*NULSYMBSLOT*npuschInfo.Qm;                        % Number of available bits per RU
        NPUSCH.CodedTrBlkSize = npuschInfo.NRU*G;                      % Coded transport block size

        NPUSCH.NRU = npuschInfo.NRU;        
        NPUSCH.IRU = npuschInfo.IRU;        
        
        NPUSCH.Qm = npuschInfo.Qm;

        NPUSCH.NRUPerNPDSCH = npuschInfo.NREP*npuschInfo.NRU;
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
                
        for IREP=vIREP                         
            
            npuschInfo.IREP = IREP;
            NPUSCH.NREP = npuschInfo.NREP;
            NPUSCH.IREP = npuschInfo.IREP;
            
            for SNR = vSNR                
                createTask(job, @runSimulation, 5, {NPUSCH, SNR, enb, numTrBlks });
                %[rIMCS rIRU rIREP rSNR rbler] = runSimulation(NPUSCH, SNR, enb, numTrBlks );
                %vOut=[vOut; rIMCS rIRU rIREP rSNR rbler]                
            end                        
        end
    end
end

submit(job);
wait(job);
y = fetchOutputs(job);
save('npuschResults6.mat','y')
delete(job);
%cat(2, y{:})  % Concatenate all the cells in y into one column vector.

