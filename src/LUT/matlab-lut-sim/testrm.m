coded=randi([0 1],132,1);
matched=nbiotLteRateMatchTurbo(coded,122,2,0);

softMatched=-2*matched+1;

unmatched=nbiotLteRateRecoverTurbo(softMatched,16,2,0);