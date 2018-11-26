%% NB-IoT NPDSCH Block Error Rate Simulation and Waveform Generation
% This example shows how LTE System Toolbox(TM) can be used to create a
% NB-IoT Narrowband Physical Downlink Shared Channel (NPDSCH) Block Error
% Rate (BLER) simulation under Additive White Gaussian Noise (AWGN), and
% generate the NB-IoT downlink time-domain waveform containing the NPDSCH
% and the narrowband reference signal (NRS).

% Copyright 2017 The MathWorks, Inc.

%% Introduction
% 3GPP Release 13 of LTE started to add support for Narrowband IoT
% applications. Release 13 defines a single NB-IoT UE Category, namely
% Cat-NB1, and Release 14 adds Cat-NB2 which allows for larger transport
% block sizes. This example focuses on Release 13 NB-IoT.
%
% The first part of the example generates a NB-IoT NPDSCH BLER curve for a
% number of SNR points and transmission parameters. The second part of the
% example generates the NB-IoT downlink time-domain waveform containing the
% NPDSCH and the NRS.
%
% This example is based on the following assumptions:
%
% * The NB-IoT operation mode is either stand-alone or guard-band, thus the
% NPDSCH occupies all the OFDM symbols of a subframe, the time-domain
% mapping is performed according to the first equation in 3GPP TS 36.211
% 10.2.8 [ <#20 2> ], and the cell-specific reference signal (CRS) is not
% transmitted.
% * The NPDSCH transmission gap is not considered and NPDSCH together with
% NRS are assumed to be transmitted in all subframes.


%% Simulation Configuration
% The simulation length is 50 DLSCH transport blocks for a number of SNR
% points. A larger number of |numTrBlks| should be used to produce
% meaningful throughput results. |SNR| can be an array of values or a
% scalar.
%function [fbler] = CustomNPDSCHBlockErrorRateExample2(IMCSIndex,ISFIndex)

numTrBlks = 2^15;                % Number of simulated transport blocks 
ISF = 0:7;                       % Resource assignment field in DCI (DCI format N1 or N2)
%IMCS =  0:12;
IMCS =  6:12;
SNR = -8:1:2;                  % SNR range in dB


%flatten for loop
flatArguments=[]
i=1;
for IMCSIndexB = 1:numel(IMCS)
     for ISFIndexB = 1:numel(ISF)
         for snrIdxB = 1:numel(SNR)            
            flatArguments(i,:)= [IMCSIndexB ISFIndexB snrIdxB ];            
            i=i+1;
         end
     end
end


bler = nan * ones(numel(IMCS),numel(ISF),numel(SNR));
%load('partial.mat');
flatbler=reshape(bler,size(flatArguments,1),1,1);

% 
% for IMCSIndex = 1:numel(IMCS)
%     for ISFIndex = 1:numel(ISF)        
%         for snrIdx = 1:numel(SNR)   

%parfor sIdx = 1:size(flatArguments,1)
for sIdx = 1:size(flatArguments,1)
    
    [ IMCSIndex ISFIndex snrIdx] = deal( flatArguments(sIdx,1), flatArguments(sIdx,2), flatArguments(sIdx,3))
    
        
%% Setup Higher Layer Parameters 
% Setup the following higher layer parameters which are used to configure
% the NPDSCH in the next section:
%
% * The variable |NPDSCHScheme| indicates whether the NPDSCH transmission
% carries the SystemInformationBlockType1-NB (SIB1-NB) or not, and whether
% the NPDSCH transmission carries the broadcast control channel (BCCH) or
% not. The allowed values of |NPDSCHScheme| are |'CarrySIB1NB'|,
% |'CarryBCCHNotSIB1NB'| and |'NotCarryBCCH'|. Note that SIB1-NB belongs to
% the BCCH.
% * The presence of SIB1-NB in the NPDSCH affects the number of NPDSCH
% repetitions and the transport block size (TBS) (see 3GPP TS 36.213
% 16.4.1.3 and 16.4.1.5 [ <#20 4> ]). |NPDSCHScheme| set to |'CarrySIB1NB'|
% indicates that the NPDSCH carries SIB1-NB; |NPDSCHScheme| set to either
% |'CarryBCCHNotSIB1NB'| or |'NotCarryBCCH'| indicates that the NPDSCH does
% not carry SIB1-NB.
% * The presence of BCCH in the NPDSCH has an effect in the NPDSCH
% repetition pattern and the scrambling sequence generation (see 3GPP TS
% 36.211 10.2.3 [ <#20 2> ]). |NPDSCHScheme| set to either |'CarrySIB1NB'|
% or |'CarryBCCHNotSIB1NB'| indicates that the NPDSCH carries BCCH;
% |NPDSCHScheme| set to |'NotCarryBCCH'| indicates that the NPDSCH does not
% carry BCCH.

NPDSCHScheme = 'NotCarryBCCH';  % The allowed values are 'CarrySIB1NB', 'CarryBCCHNotSIB1NB' or 'NotCarryBCCH'

%%
% * The variable |ISF| configures the number of subframes for a NPDSCH
% according to 3GPP TS 36.213 Table 16.4.1.3-1 [ <#20 4> ]. Valid values
% for |ISF| are 0...7.
% 
% When the NPDSCH carries the SIB1-NB:
%
% * The variable |SchedulingInfoSIB1| configures the number of NPDSCH
% repetitions according to 3GPP TS 36.213 Table 16.4.1.3-3 and the TBS
% according to Table 16.4.1.5.2-1 [ <#20 4> ]. Valid values for
% |SchedulingInfoSIB1| are 0...11.
%
% When the NPDSCH does not carry the SIB1-NB:
%
% * The variable |IREP| configures the number of NPDSCH repetitions
% according to 3GPP TS 36.213 Table 16.4.1.3-2 [ <#20 4> ]. Valid values
% for |IREP| are 0...15.
% * The variable |IMCS| together with |IREP| configure the TBS according to
% 3GPP TS 36.213 Table 16.4.1.5.1-1 [ <#20 4> ]. Valid values for |IMCS|
% are 0...12.

%ISF = 6;                       % Resource assignment field in DCI (DCI format N1 or N2)
SchedulingInfoSIB1 = 0;        % Scheduling information field in MasterInformationBlock-NB (MIB-NB)
IREP = 1;                      % Repetition number field in DCI (DCI format N1 or N2)
%IMCS = 0;                      % Modulation and coding scheme field in DCI (DCI format N1 or N2)

%% eNB Configuration 
% Configure the starting frame and subframe numbers in the simulation for
% each SNR point, the narrowband physical cell ID, cyclic prefix format and
% the number of NRS antenna ports. One antenna port indicates port 2000 is
% used, two antenna ports indicates port 2000 and port 2001 are used.
% Referencia de antenas http://rfmw.em.keysight.com/wireless/helpfiles/89600b/webhelp/Subsystems/lte/content/lte_antenna_paths_ports_explanation.htm
% For exact information about what is possible in LTE, see 3GPP TS 36.211 and 36.213. 

enb.NFrame = 0;                % Frame number to start with the simulation
enb.NSubframe = 0;             % Subframe number to start with the simulation
enb.NNCellID = 0;              % NB-IoT physical cell ID
%enb.CyclicPrefixUL = 'Normal'; % NB-IoT only support normal cyclic prefix
enb.CellRefP = 1;              % Number of NRS antenna ports, should be either 1 or 2

%% NPDSCH Configuration

%%
% Create a class instance |npdschInfo| with default NPDSCH parameters using
% the class |hNPDSCHInfo|, then the configured higher layer parameters are
% used to obtain the following NPDSCH parameters in the class:
%
% * The number of repetitions (|NREP|)
% * The number of subframe s used for a NPDSCH when there is no repetition
% (|NSF|)
% * The transport block size (|TBS|)
%
% The method displaySubframePattern in the class |hNPDSCHInfo| can display
% the NPDSCH repetition pattern, which is shown in the next section.
%
% Note: When NPDSCH does not carry the SIB1-NB, an error is triggered if
% the configured |IREP| and |IMCS| values lead to an empty TBS. This is the
% case when the TBS is not defined for a particular |IREP| and |IMCS| pair
% in 3GPP TS 36.213 table 16.4.1.5.1-1 [ <#20 4> ].

npdschInfo = hNPDSCHInfo;
npdschInfo.Scheme = NPDSCHScheme;
npdschInfo.ISF = ISF(ISFIndex);
if strcmp(NPDSCHScheme, 'CarrySIB1NB')       % NPDSCH carrying SIB1-NB
    npdschInfo.SchedulingInfoSIB1 = SchedulingInfoSIB1;
elseif strcmp(NPDSCHScheme, 'CarryBCCHNotSIB1NB') || ...
        strcmp(NPDSCHScheme, 'NotCarryBCCH') % NPDSCH not carrying SIB1-NB
    npdschInfo.IREP = IREP;
    npdschInfo.IMCS = IMCS(IMCSIndex);
    % Verify the inputs of IREP and IMCS
    if isempty(npdschInfo.TBS)
        npdschInfo.TBSTable
        warning(['Invalid [ITBS,ISF] (where ITBS=IMCS=' num2str(IMCS(IMCSIndex))...
            ', ISF=' num2str(ISF(ISFIndex))  ') pair, empty TBS is returned, check valid pairs in the above table or 3GPP TS 36.213 table 16.4.1.5.1-1']);
        continue
    end
end

%%
% Create the structure |NPDSCH| using the obtained number of repetitions
% (|npdschInfo.NREP|), the number of subframes of a NPDSCH
% (|npdschInfo.NSF|) and the TBS (|npdschInfo.TBS|) in the class instance
% |npdschInfo|.
NPDSCH=struct()
NPDSCH.TrBlkSize = npdschInfo.TBS;                             % Transport block size
[~,info] = hNPDSCHIndices(enb);
G = info.G;                                                    % Number of available bits per subframe
NPDSCH.CodedTrBlkSize = npdschInfo.NSF*G;                      % Coded transport block size
NPDSCH.NSF = npdschInfo.NSF;
NPDSCH.NREP = npdschInfo.NREP;
NPDSCH.NRepMin = min(npdschInfo.NREP, 4);                      % Initial number of repetitions when NPDSCH does not carry BCCH
NPDSCH.NSubframesPerNPDSCH = npdschInfo.NREP*npdschInfo.NSF; % The number of subframes for a NPDSCH when considering repetitions

%%
% Verify the configured higher layer parameters using the DLSCH code rate.
% The code rate is the ratio between the number of bits after CRC coding
% and the number of bits after rate matching. For the case when |SIB1NB| is
% set to |true|, the code rate |R| can be larger than or equal to 1, which
% is not a valid scenario. For example, such case happens when |ISF| is set
% to 0 and |SchedulingInfoSIB1| is set to 3.

R = (NPDSCH.TrBlkSize+24)/NPDSCH.CodedTrBlkSize;  % DLSCH channel coding rate, 24 denotes the number of CRC bits
if R >= 1
    error(['DLSCH coding rate larger than or equal to 1 for the configured higher layer parameters. NSF = ' ...
        num2str(NPDSCH.NSF) '; TBS = ' num2str(NPDSCH.TrBlkSize) '; Coded block size = ' num2str(NPDSCH.CodedTrBlkSize) ...
        '; Rate = ' num2str(R)]);
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

NPDSCH.Modulation = 'QPSK';             % Modulation scheme (must be QPSK)
NPDSCH.RNTI = 1;                        % RNTI
if enb.CellRefP == 1
    NPDSCH.TxScheme = 'Port0';          % Transmission scheme
    NPDSCH.NLayers = 1;                 % Number of layers 
elseif enb.CellRefP == 2
    NPDSCH.TxScheme = 'TxDiversity';
    NPDSCH.NLayers = 2;                             
else
    error('Number of antenna ports is not correct, should be either 1 or 2');
end

%% Display Subframe Repetition Pattern
% The variable |displayPattern| controls the display of the NPDSCH subframe
% repetition pattern. An example is shown in the following figure for the
% case when the NPDSCH carries the BCCH, the NPDSCH consists of
% |npdschInfo.NSF=3| different subframes, each color represents a subframe
% which occupies 1 ms. Each subframe is repeated |npdschInfo.NREP=4| times,
% thus a total of 12 subframes are required to transmit the NPDSCH.

displayPattern = false;
% Display NPDSCH repetition pattern
if displayPattern == true
    npdschInfo.displaySubframePattern;
end

%% Block Error Rate Simulation Loop
% This part of example shows how to perform NB-IoT NPDSCH link level
% simulation and plot BLER results. The transmit and receive chain is
% depicted in the following figure. A random stream of bits with the size
% of the desired transport block undergoes CRC encoding, convolutional
% encoding and rate matching to obtain the NPDSCH bits, which are repeated
% according to a specific subframe repetition pattern. Scrambling,
% modulation, layer mapping and precoding are then applied to form the
% complex NPDSCH symbols. AWGN is added to these symbols after which
% channel decoding and demodulation are performed to recover the transport
% block. After de-scrambling, the repetitive subframes are soft-combined
% before rate recover. The transport block error rate is calculated for
% each SNR point.
%
% <<NPDSCHTransmitAndReceiveChain.png>>

NSubframe = enb.NFrame*10+enb.NSubframe;                   % Absolute subframe number at the starting point of the simulation
TotSubframes = NPDSCH.NSubframesPerNPDSCH*numTrBlks;       % Calculate total number of subframes to simulate                                % Initialize BLER result

% Initialize the transmitted NPDSCH symbols for all subframes, it is used
% for waveform generation later in the second part of the example
txNpdschSymbolsAllSubframes = [];                      

% The temporary variable 'enb_init' is used to create the temporary
% variable 'enb' within the SNR loop to create independent simulation loops
% for the 'parfor' loop
enb_init = enb;


%parfor snrIdx = 1:numel(SNR)
% To enable the use of parallel computing for increased speed comment out
% the 'for' statement above and uncomment the 'parfor' statement below.
% This needs the Parallel Computing Toolbox. If this is not installed
% 'parfor' will default to the normal 'for' statement.

    if ~ isnan(flatbler(sIdx))
        continue
    end


    % Set the random number generator seed depending to the loop variable
    % to ensure independent random streams
    tStart=tic
    
    rng(snrIdx,'combRecursive');
       
    %print stitle
    
    enb = enb_init;                                    % Initialize eNB configuration
    npdschSubframeIdx = 0;                             % 0-based subframe index for a transport block (with NPDSCH repetitions)
    txCodedTrblk = [];                                 % Initialize the transmitted coded transport block
    rxCodedTrblk = zeros(NPDSCH.CodedTrBlkSize,1);     % Pre-allocate the received coded transport block after soft-combing
    scrambleSeq = [];                                  % Initialize the scrambling sequence at transmitter
    scrambleSeqRx = [];                                % Initialize the scrambling sequence at receiver
    numBlkErrors = 0;                                  % Number of transport blocks with errors
    
%     h = waitbar(0,'Initializing...');
    
    for subframeIdx=NSubframe:(NSubframe+TotSubframes)-1
        
%         
%         if mod(subframeIdx,5123200)==0
%             waitbar(subframeIdx/(NSubframe+TotSubframes-1),h,stitle);
%         end
        
        % Update subframe number and frame number
        enb.NSubframe = mod(subframeIdx,10);
        enb.NFrame = floor(subframeIdx/10);

        % Get subframe index p for a NPDSCH when there is no repetition.
        if strcmp(NPDSCHScheme,'CarrySIB1NB') || ...
                strcmp(NPDSCHScheme,'CarryBCCHNotSIB1NB')  % NPDSCH carrying BCCH
            p = mod(npdschSubframeIdx,NPDSCH.NSF);
        elseif strcmp(NPDSCHScheme,'NotCarryBCCH')         % NPDSCH not carrying BCCH
            p = mod(floor(npdschSubframeIdx/NPDSCH.NRepMin),NPDSCH.NSF);
        end
        
        % Generate scrambling sequence for transmitter and receiver
        if isempty(scrambleSeq)
            if strcmp(NPDSCHScheme,'CarrySIB1NB') ||...    % NPDSCH carrying BCCH
                    strcmp(NPDSCHScheme,'CarryBCCHNotSIB1NB')
                cinit = 2^15*NPDSCH.RNTI+(enb.NNCellID+1)*(mod(enb.NFrame,61)+1);
            elseif strcmp(NPDSCHScheme,'NotCarryBCCH')     % NPDSCH not carrying BCCH
                cinit = 2^14*NPDSCH.RNTI+mod(enb.NFrame,2)*2^13+enb.NSubframe*2^9+enb.NNCellID;
            end
            scrambleSeq = ltePRBS(cinit,NPDSCH.CodedTrBlkSize);
            scrambleSeqRx = ltePRBS(cinit,NPDSCH.CodedTrBlkSize,'signed');
        end
        
        % Update transport block when its transmission is finished
        if isempty(txCodedTrblk)
            % Generate bits for a transport block
            txTrBlk = randi([0 1],NPDSCH.TrBlkSize,1);
            % Transport block CRC attachment
            crced = lteCRCEncode(txTrBlk,'24A');
            % Channel coding
            coded = lteConvolutionalEncode(crced);
            % Rate matching
            txCodedTrblk = lteRateMatchConvolutional(coded,NPDSCH.CodedTrBlkSize);
        end
        % Scrambling the coded block transmitted in a subframe
        scrambledCws = xor(txCodedTrblk(1+p*G:(p+1)*G), scrambleSeq(1+p*G:(p+1)*G));
        % Modulation
        npdschSymbols = lteSymbolModulate(scrambledCws,NPDSCH.Modulation);
        % Layer mapping
        layerMappedSymbols = lteLayerMap(NPDSCH,npdschSymbols); 
        % Precoding
        txNpdschSymbols = lteDLPrecode(enb,NPDSCH,layerMappedSymbols); 
        
        % Save the transmitted symbols for all subframes for the first
        % simulated SNR point
        if snrIdx == 1
            txNpdschSymbolsAllSubframes = [txNpdschSymbolsAllSubframes txNpdschSymbols]; %#ok<AGROW>
        end
        
        % Get SNR in linear form, generate and add noise
        snr = 10.^(SNR(snrIdx)/10);
        npdschSize = size(txNpdschSymbols);
        noise = (1/2)*sqrt(1/snr)*complex(randn(npdschSize),randn(npdschSize));
        rxNpdschSymbols = txNpdschSymbols + noise;
        
        % Deprecoding (pseudo-inverse based) 
        rxDeprecoded = lteDLDeprecode(enb,NPDSCH,rxNpdschSymbols);
        % Layer demapping
        symCombining = lteLayerDemap(NPDSCH,rxDeprecoded);  
        % Soft demodulation of received symbols
        demodpdschSymb = lteSymbolDemodulate(symCombining{1},NPDSCH.Modulation,'Soft'); 
        % Get scrambling sequence for descrambling in a subframe
        scrambleSeqSubframe = scrambleSeqRx(1+p*G:(p+1)*G);
        % Descrambling of the received subframe and soft-combine the
        % repeated subframes
        rxCodedTrblk(1+G*p:(p+1)*G)=rxCodedTrblk(1+G*p:(p+1)*G)+demodpdschSymb.*scrambleSeqSubframe;
        % Increase the subframe counter by 1
        npdschSubframeIdx = npdschSubframeIdx + 1;
        
        % Decode the transport block when all its related subframes have
        % been received
        if npdschSubframeIdx == NPDSCH.NSubframesPerNPDSCH
           % Rate-recover
           sfbitsRateRecovered = lteRateRecoverConvolutional(rxCodedTrblk,3*(NPDSCH.TrBlkSize+24));
           % Viterbi decode
           bitsDecoded = lteConvolutionalDecode(sfbitsRateRecovered);
           % CRC decode
           [rxTrBlk,err] = lteCRCDecode(bitsDecoded,'24A');
           
           if err ~= 0
               numBlkErrors=numBlkErrors+1;
           end
           % Re-initialization
           npdschSubframeIdx = 0;
           txCodedTrblk = [];
           rxCodedTrblk = zeros(NPDSCH.CodedTrBlkSize,1);
        end
        
        % Scrambling sequence re-initialization
        if strcmp(NPDSCHScheme,'CarrySIB1NB') ||...   
                strcmp(NPDSCHScheme,'CarryBCCHNotSIB1NB') % NPDSCH carrying BCCH
            if mod(npdschSubframeIdx, NPDSCH.NSF) == 0
                scrambleSeq = [];
                scrambleSeqRx = [];
            end
        elseif strcmp(NPDSCHScheme,'NotCarryBCCH')        % NPDSCH not carrying BCCH
            if mod(npdschSubframeIdx, NPDSCH.NRepMin*NPDSCH.NSF) == 0
                scrambleSeq = [];
                scrambleSeqRx = [];
            end
        end
    end
    
%     close(h)
    
    flatbler(sIdx) = numBlkErrors/numTrBlks;    
    t = getCurrentTask();    
    %parsave('partial2.mat','flatbler')
    stitle=sprintf('Simulating at IMSC:%g ISF:%g %gdB SNR , result %g, thread %g, elapsed %g' ,IMCS(IMCSIndex),ISF(ISFIndex),SNR(snrIdx),  flatbler(sIdx), t.ID, toc(tStart));
    disp(stitle)    
end

% %% Plot Block Error Rate vs SNR Results
% figure;
% semilogy(SNR, bler, '-ob');
% grid on;
% xlabel('SNR (dB)');
% ylabel('BLER');
% 
% if strcmp(NPDSCHScheme,'CarrySIB1NB') ||...
%         strcmp(NPDSCHScheme,'CarryBCCHNotSIB1NB')         % NPDSCexH carrying BCCH
%     if strcmp(NPDSCH.TxScheme,'Port0')
%         title(['NPDSCH carrying BCCH: TBS=' num2str(NPDSCH.TrBlkSize)...
%             '; NSF=' num2str(NPDSCH.NSF) '; NREP=' num2str(NPDSCH.NREP) ...
%             '; TxScheme=Port2000']);
%     elseif strcmp(NPDSCH.TxScheme,'TxDiversity')
%         title(['NPDSCH carrying BCCH: TBS=' num2str(NPDSCH.TrBlkSize)...
%             '; NSF=' num2str(NPDSCH.NSF) '; NREP=' num2str(NPDSCH.NREP) ...
%             '; TxScheme=' NPDSCH.TxScheme]);
%     end
% elseif strcmp(NPDSCHScheme,'NotCarryBCCH')                % NPDSCH not carrying BCCH
%     if strcmp(NPDSCH.TxScheme,'Port0')
%         title(['NPDSCH not carrying BCCH: TBS=' num2str(NPDSCH.TrBlkSize)...
%             '; NSF=' num2str(NPDSCH.NSF) '; NREP=' num2str(NPDSCH.NREP) ...
%             '; TxScheme=Port2000']);
%     elseif strcmp(NPDSCH.TxScheme,'TxDiversity')
%         title(['NPDSCH not carrying BCCH: TBS=' num2str(NPDSCH.TrBlkSize)...
%             '; NSF=' num2str(NPDSCH.NSF) '; NREP=' num2str(NPDSCH.NREP) ...
%             '; TxScheme=' NPDSCH.TxScheme]);
%     end
% end

% end
% end
save('blerResults.mat','flatbler','IMCS','SNR','ISF')

% return
% %%
% % For a longer simulation with |numTrBlks| set to 5000, the BLER plot
% % becomes:
% %
% % <<exampleLongRun5000trblks.png>>
% 
% %% Waveform Generation
% % This part of the example shows how to generate a NB-IoT downlink waveform
% % containing the NPDSCH and the NRS. The procedure is depicted in the
% % following figure. The complex NPDSCH symbols generated in the BLER
% % simulation together with the NRS symbols are mapped to the frequency
% % grid, which is then converted to a time-domain waveform.
% %
% % <<NPDSCHWaveformGeneration.png>>
% 
% subframe = zeros(12,14,enb.CellRefP);                     % Pre-allocate the transmitted frequency grid of a subframe
% txGrid = [];                                              % Initialize the transmitted frequency grid
% counter = 0;                                              % Initialize the counter for NPDSCH symbol extraction for a subframe
% for subframeIdx=NSubframe:(NSubframe+TotSubframes)-1
% 
%     % Update subframe number and frame number
%     enb.NSubframe = mod(subframeIdx,10);
%     enb.NFrame = floor(subframeIdx/10);
% 
%     % Generate NPDSCH indices
%     pdschIndices = hNPDSCHIndices(enb);
%     
%     % Extract the NPDSCH symbols for a subframe from the pre-saved signal
%     % in the BLER simulation
%     txNpdschSymbols = txNpdschSymbolsAllSubframes(:,(1:enb.CellRefP)+counter*enb.CellRefP);
%     
%     % NPDSCH symbols mapping on resource grid is performed using NPDSCH indices.
%     subframe(pdschIndices) = txNpdschSymbols;
%     
%     % NRS symbol generation. These symbols are then mapped onto resource
%     % elements (REs) of a resource grid with the help of linear indices.
%     NRSindices = hNRSIndices(enb);
%     NRSsymbols = hNRS(enb);
%     subframe(NRSindices) = NRSsymbols;
% 
%     % Concatenating subframes to form a complete frame
%     txGrid = cat(2,txGrid,subframe);
%     
%     % Increase the counter
%     counter = counter+1;
% 
% end
% 
% %%
% % Apply the default window size according to 3GPP TS 36.104 Table E.5.1-1a
% % [ <#20 1> ]
% if(~isfield(enb,'Windowing'))
%     enb.Windowing = 6;
% end
% 
% %%
% % Time domain mapping is performed according to the first equation in 3GPP
% % TS 36.211 10.2.8 [ <#20 2> ], based on the assumption that the considered
% % NB-IoT operation mode in this example is either stand-alone or
% % guard-band. The mapping is the same as that in the LTE SC-FDMA uplink,
% % but in this case a single physical resource block is used. The bandwidth
% % of the signal is 180kHz, i.e. 12 subcarriers with subcarrier spacing of
% % 15kHz.
% 
% [timeDomainWaveform, infoOFDM] = lteSCFDMAModulate(enb,txGrid);
% 
% %%
% % Display the spectrum of the generated signal. As shown in the figure
% % below, the spectrum centered at 0kHz has a bandwidth of 180kHz with power
% % above -30dBm, which indicates the narrowband nature of the NB-IoT signal.
% 
% spectrumAnalyzer = dsp.SpectrumAnalyzer;
% spectrumAnalyzer.ShowLegend = true;
% if enb.CellRefP == 1
%     spectrumAnalyzer.ChannelNames = {'NB-IoT Downlink Spectrum at Antenna Port 2000'};
% elseif enb.CellRefP == 2
%     spectrumAnalyzer.ChannelNames = {'NB-IoT Downlink Spectrum at Antenna Port 2000',...
%         'NB-IoT Downlink Spectrum at Antenna Port 2001'};
% end
% spectrumAnalyzer.SampleRate = infoOFDM.SamplingRate;
% spectrumAnalyzer(timeDomainWaveform);
% 
% %% Appendix
% % This example uses the helper class and functions:
% %
% % * <matlab:edit('hNPDSCHInfo.m') hNPDSCHInfo.m>
% % * <matlab:edit('hNPDSCHIndices.m') hNPDSCHIndices.m>
% % * <matlab:edit('hNRSIndices.m') hNRSIndices.m>
% % * <matlab:edit('hNRS.m') hNRS.m>
% 
% %% Selected Bibliography
% % # 3GPP TS 36.104 "Base Station (BS) radio transmission and reception"
% % # 3GPP TS 36.211 "Physical channels and modulation"
% % # 3GPP TS 36.212 "Multiplexing and channel coding"
% % # 3GPP TS 36.213 "Physical layer procedures"
% 
% displayEndOfDemoMessage(mfilename)