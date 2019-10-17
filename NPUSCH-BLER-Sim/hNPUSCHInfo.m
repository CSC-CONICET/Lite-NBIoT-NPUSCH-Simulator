% NB-IoT NPDSCH Information
%
% The class provides NPDSCH related information: the number of
% subframes for a NPDSCH (NSF), the number of repetitions for NPDSCH
% transmission (NREP), the transport block size (TBS) and subframe
% pattern for NPDSCH transmission, based on a set of chosen parameters:
% Scheme, ISF, IREP, IMCS and SchedulingInfoSIB1. 
%
% Scheme indicates whether the NPDSCH transmission carries
% SystemInformationBlockType1-NB (SIB1-NB) or not, and whether the NPDSCH
% transmission carries the broadcast control channel (BCCH) or not. The
% allowed values are 'CarrySIB1NB', 'CarryBCCHNotSIB1NB' and
% 'NotCarryBCCH'. Note that SIB1-NB belongs to BCCH. When NPDSCH carries
% SIB1-NB, use ISF and SchedulingInfoSIB1 to control NSF, NREP and TBS;
% When NPDSCH does not carry SIB1-NB, use ISF, IREP and IMCS to control
% NSF, NREP and TBS.
%
% Note: TBS may be returned as empty when NPDSCH does not carry SIB1-NB,
% e.g., when ISF = 4 and IMCS = 9, no TBS is defined.

%   Copyright 2017 The MathWorks, Inc.

classdef hNPUSCHInfo
    
    properties (Dependent)
        %Scheme; % Charactor vector to describe whether NDSCH carries SIB1 and BCCH or not
        IRU;    % Index of the number of subframes for a NPDSCH (0,1,...,6,7)
        IREP;   % Index of the number of repetitions for NPDSCH transmission (0,1,...,14,15)
        IMCS;   % Index of the modulation and coding scheme (0,1,...,11,12)        
        %SchedulingInfoSIB1; % Value of schedulingInfoSIB1 (0,1,...,10,11)
    end

    properties (Access=private)
        %pScheme = 'CarryBCCHNotSIB1NB';
        pIRU = 1;
        pIREP = 1;
        pIMCS = 1;
        %pSchedulingInfoSIB1 = 0;
    end
    
    properties (Access=public)
        %pScheme = 'CarryBCCHNotSIB1NB';
        MONO = 1;        
    end
    
    properties(Dependent,SetAccess = private) 
        %BCCH; % NPDSCH transmission carrying BCCH or not (true or false)
        %SIB1NB; % NPDSCH transmission carrying SystemInformationBlockType1-NB or not (true or false)
        ITBS; % Index of tranport block size
        TBS;  % Tranport block size
        NRU;  % Number of subframes for a NPDSCH 
        NREP; % Number of repetitions for NPDSCH transmission
        Qm;
    end
    
    properties (Constant,Access=public)
        NRUTable = getNRUTable(); % TS 36.213 Table 16.4.1.3-1: Number of subframes (NSF) for NPDSCH
        NREPTable = getNREPTable(); % TS 36.213 Table 16.4.1.3-2: Number of repetitions (NREP) for NPDSCH
        TBSTable = getTBSTable(); % TS 36.213 Table 16.4.1.5.1-1: Transport block size (TBS) table
        ITBSTable = getITBSTable();
        QmTable = getQmTable();
        %NREPTableSIB1 = getSchedulingInfoNReptable(); % TS 36.213 Table 16.4.1.3-3: Number of repetitions for NPDSCH carrying SystemInformationBlockType1-NB
        %TBSTableSIB1 = getSchedulingInfoTBStable(); % TS 36.213 Table 16.4.1.5.2-1: Transport block size (TBS) table for NPDSCH carrying SystemInformationBlockType1-NB
    end
    
    methods
        

        function param = get.ITBS(obj)
            param = [];
            if (obj.MONO)
                 m = (obj.ITBSTable.IMSC == obj.IMCS);
                 if any(m)
                     param = obj.ITBSTable.ITBS(m);                     
                 end
            else
                param = obj.IMCS;
            end
        end
        
        function t = get.TBS(obj)
                m = (obj.TBSTable.ITBS==obj.ITBS) & (obj.TBSTable.IRU==obj.IRU);
                if any(m)
                    t = obj.TBSTable.TBS(m);
                else
                    t = [];
                end
        end
        
        function n = get.NRU(obj)
            m = obj.NRUTable.IRU==obj.IRU;
            n = obj.NRUTable.NRU(m);
        end
        
        function n = get.NREP(obj)
                m = obj.NREPTable.IREP==obj.IREP; 
                n = obj.NREPTable.NREP(m);
        end
        
        function n = get.Qm(obj)            
            if (obj.MONO)
                m = obj.QmTable.IMCS==obj.IMCS;
                n = obj.QmTable.Qm(m);
            else
                n=2;
            end 
        end     
        
    end
        

    methods 
         
        % Setter associated with the IRU parameter
        function obj = set.IRU(obj,param) 
            m = obj.NRUTable.IRU==param;
            if ~any(m)
                error(['IREP is not one of the set {' num2str(obj.NRUTable.IRU.') '}.']);
            end
            obj.pIRU = param;
        end
        % Getter associated with the IRU parameter
        function param = get.IRU(obj)     
            param = obj.pIRU;      
        end
        
        % Setter associated with the IREP parameter
        function obj = set.IREP(obj,param)
            m = obj.NREPTable.IREP==param;
            if ~any(m)
                error(['IREP is not one of the set {' num2str(obj.NREPTable.IREP.') '}.']);
            end
            obj.pIREP = param;
        end
        % Getter associated with the IREP parameter
        function param = get.IREP(obj)     
            param = obj.pIREP;      
        end
        
        % Setter associated with the IMCS parameter
        function obj = set.IMCS(obj,param)             
            m = unique(obj.TBSTable.ITBS)==param;
            if ~any(m)
                error(['IMCS is not one of the set {' num2str(unique(obj.TBSTable.ITBS).') '}.']);
            end
            obj.pIMCS = param;
        end
        
        % Getter associated with the IMCS parameter
        function param = get.IMCS(obj)     
            param = obj.pIMCS;      
        end
        
    end
    
end

function tab = getNRUTable()
    IRU=(0:7).'; 
    NRU=[1:6 8 10].';
    tab = table(IRU,NRU);
    tab.Properties.Description = 'TS 36.213 Table 16.5.1.1-2: Number of resource units ( NRU ) for NPUSCH.';
end

function tab = getNREPTable()
    IREP=(0:7).'; 
    NREP=[1 2 4 8 16 32 64 128].';
    tab = table(IREP,NREP);
    tab.Properties.Description = 'TS 36.213 Table 16.5.1.1-3: Number of repetitions ( N Rep ) for NPUSCH';
end


function tab = getITBSTable()
    IMSC=(0:10).';
    ITBS=[0 2 1 3:10].';
    tab = table(IMSC,ITBS);
    tab.Properties.Description = 'Table 16.5.1.2-1: Modulation and TBS index table for NPUSCH with N_sc^RU = 1';
end

function tab = getQmTable()
    IMCS=(0:10).'; 
    Qm=[1 1 2 2 2 2 2 2 2 2 2].';
    tab = table(IMCS,Qm);
    tab.Properties.Description = 'Table 16.5.1.2-1: Modulation and TBS index table for NPUSCH with N_sc^RU = 1';
end

function tab = getTBSTable()
    IRU=[ 0:7 0:7 0:7 0:7 0:7 0:7 0:7 0:7 0:7 0:7 0:7 0:7 0:7 0:7].';
    ITBS=[ 0*ones(1,8)  1*ones(1,8)  2*ones(1,8)  3*ones(1,8) ...
           4*ones(1,8)  5*ones(1,8)  6*ones(1,8)  7*ones(1,8) ...
           8*ones(1,8)  9*ones(1,8) 10*ones(1,8) 11*ones(1,8) ...
          12*ones(1,8) 13*ones(1,8) ].';
      
    TBS=[16  32  56   88  120  152  208  256 ...
         24  56  88  144  176  208  256  344 ...
         32  72 144  176  208  256  328  424 ...
        40 104 176  208  256  328  440  568 ...
         56 120 208  256  328  408  552  680 ...
         72 144 224  328  424  504  680  872 ...
         88 176 256  392  504  600  808 1000 ...
        104 224 328  472  584  712 1000 1224 ...
        120 256 392  536  680  808 1096 1384 ...
        136 296 456  616  776  936 1256 1544 ...
        144 328 504  680  872 1000 1384 1736 ...
        176 376 584  776 1000 1192 1608 2024 ...
        208 440 680 1000 1128 1352 1800 2280 ...
        224 488 744 1032 1256 1544 2024 2536 ].';
    tab = table(ITBS,IRU,TBS);
    tab.Properties.Description = 'TS 36.213 Table 16.4.1.5.1-1: Transport block size (TBS) table';
end