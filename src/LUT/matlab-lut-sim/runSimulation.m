function [IMCS IRU IREP SNR bler] = runSimulation( NPUSCH, SNR, enb, numTrBlks)

            %parfor snrIdx = 1:numel(SNR)
            % To enable the use of parallel computing for increased speed comment out
            % the 'for' statement above and uncomment the 'parfor' statement below.
            % This needs the Parallel Computing Toolbox. If this is not installed
            % 'parfor' will default to the normal 'for' statement.

                % Set the random number generator seed depending to the loop variable
                % to ensure independent random streams
                IMCS=NPUSCH.IMCS;
                IRU=NPUSCH.IRU;
                IREP=NPUSCH.IREP;
                bler=nan;
                outFileName=sprintf('%i_%i_%i_%f.csv',[IMCS IRU IREP SNR]); 
                
                if exist(outFileName, 'file') 
                    return
                end
                
                rng('shuffle','combRecursive');

                fprintf('\nSimulating at %gdB SNR\n' ,SNR);
                
                txCodedTrblk = [];                                 % Initialize the transmitted coded transport block
                rxCodedTrblk = zeros(NPUSCH.CodedTrBlkSize,1);     % Pre-allocate the received coded transport block after soft-combing                                
                scrambleSeq = [];                                  % Initialize the scrambling sequence at transmitter
                scrambleSeqRx = [];                                % Initialize the scrambling sequence at receiver
                numBlkErrors = 0;                                  % Number of transport blocks with errors

                for blockIdx=[1:numTrBlks]        

                    % Update subframe number and frame number
                    %enb.NSubframe = mod(subframeIdx,10);
                    %enb.NFrame = floor(subframeIdx/10);

                    % Get subframe index p for a NPDSCH when there is no repetition.
            %         if strcmp(NPDSCHScheme,'CarrySIB1NB') || ...
            %                 strcmp(NPDSCHScheme,'CarryBCCHNotSIB1NB')  % NPDSCH carrying BCCH
            %             p = mod(npdschSubframeIdx,NPDSCH.NSF);
            %         elseif strcmp(NPDSCHScheme,'NotCarryBCCH')         % NPDSCH not carrying BCCH
            %             p = mod(floor(npdschSubframeIdx/NPDSCH.NRepMin),NPDSCH.NSF);
            %         end

                    % Generate bits for a transp nort block
                    txTrBlk = randi([0 1],NPUSCH.TrBlkSize,1);
                    % Transport block CRC attachment
                    crced = lteCRCEncode(txTrBlk,'24A');
                    % Channel coding
                    coded = lteTurboEncode(crced);
                    
                    sfbitsRateRecovered=zeros(size(coded)); % Reinitialize soft combining buffer
                                        
            
                    for rep = [0:NPUSCH.NREP-1]
                        NPUSCH.rv=mod(rep,2)*2; %Redundacy version rota entre 0 y 2 para cada paquete                        
                        
                        % Rate matching
                        % Generate scrambling sequence for transmitter and receiver
                        %TODO: La secuencia deberia cambiar con cada codeword y cada repetición.                        
                        txCodedTrblk = nbiotLteRateMatchTurbo(coded,NPUSCH.CodedTrBlkSize,NPUSCH.Qm,NPUSCH.rv);                        
                        
                        
                        %if isempty(scrambleSeq)            
                        cinit = 2^14*NPUSCH.RNTI+mod(enb.NFrame,2)*2^13+enb.NSubframe*2^9+enb.NNCellID;
                        scrambleSeq = ltePRBS(cinit,NPUSCH.CodedTrBlkSize);
                        scrambleSeqRx = ltePRBS(cinit,NPUSCH.CodedTrBlkSize,'signed');
                        %end

                        % Scrambling the coded block transmitted in a subframe
                        scrambledCws = xor(txCodedTrblk, scrambleSeq);
                        % Modulation
                        txNpuschSymbols = lteSymbolModulate(scrambledCws,NPUSCH.Modulation);

                        % Layer mapping
                        %layerMappedSymbols = lteLayerMap(NPUSCH,npuschSymbols); 
                        % Precoding
                        %txNpdschSymbols = lteDLPrecode(enb,NPDSCH,layerMappedSymbols); 

                        % Get SNR in linear form, generate and add noise
                        snr = 10.^(SNR/10);
                        npuschSize = size(txNpuschSymbols);                                                
                        
                        noise = (1/2)*sqrt(1/snr)*complex(randn(npuschSize),randn(npuschSize));
                        rxNpuschSymbols = txNpuschSymbols + noise;

                        % Deprecoding (pseudo-inverse based) 
                        %rxDeprecoded = lteDLDeprecode(enb,NPDSCH,rxNpdschSymbols);
                        % Layer demapping
                        %symCombining = lteLayerDemap(NPDSCH,rxDeprecoded);  
                        % Soft demodulation of received symbols
                        demodpdschSymb = lteSymbolDemodulate(rxNpuschSymbols,NPUSCH.Modulation,'Soft'); 
                        % Get scrambling sequence for descrambling in a subframe
                        %scrambleSeqSubframe = scrambleSeqRx(1+p*G:(p+1)*G);
                        % Descrambling of the received subframe 
                        % repeated subframes
                        rxCodedTrblk=demodpdschSymb.*scrambleSeqRx;

                        % Rate-recover
                        sfbitsRateRecovered = sfbitsRateRecovered + nbiotLteRateRecoverTurbo(rxCodedTrblk ,NPUSCH.TrBlkSize,NPUSCH.Qm,NPUSCH.rv);
                        
                        
                        %soft-combine
                        
                        % Increase the subframe counter by 1

                        enb.NFrame=enb.NFrame+NPUSCH.NRU;
                    end


                    % Decode the transport block when all its related subframes have
                    % been received

                       % Viterbi decode
                       bitsDecoded = lteTurboDecode(sfbitsRateRecovered);
                       % CRC decode
                         [rxTrBlk,err] = lteCRCDecode(bitsDecoded,'24A');

                       if err ~= 0
                           numBlkErrors=numBlkErrors+1;
                       end
                       % Re-initialization

                       txCodedTrblk = [];
                       rxCodedTrblk = zeros(NPUSCH.CodedTrBlkSize,1);


                    % Scrambling sequence re-initialization

            %         if strcmp(NPUSCHScheme,'CarrySIB1NB') ||...   
            %                 strcmp(NPUSCHScheme,'CarryBCCHNotSIB1NB') % NPDSCH carrying BCCH
            %             if mod(npuschSubframeIdx, NPDSCH.NSF) == 0
            %                 scrambleSeq = [];
            %                 scrambleSeqRx = [];
            %             end
            %         elseif strcmp(NPUSCHScheme,'NotCarryBCCH')        % NPDSCH not carrying BCCH
            %             if mod(npuschSubframeIdx, NPUSCH.NRepMin*NPUSCH.NSF) == 0
            %                 scrambleSeq = [];
            %                 scrambleSeqRx = [];
            %             end
            %         end

            %         scrambleSeq = ltePRBS(cinit,NPUSCH.CodedTrBlkSize);
            %         scrambleSeqRx = ltePRBS(cinit,NPUSCH.CodedTrBlkSize,'signed');
                end

                %bler(snrIdx) = numBlkErrors/numTrBlks;
                bler = numBlkErrors/numTrBlks;
                
                csvwrite(outFileName,[IMCS IRU IREP SNR bler]);
                
end       
