** Description
This is an NBIoT - NPUSCH - Block Error Rate (BLER) simulator. It was implemented in MATLAB following the standard specification up to the modulation mapping to the I/Q space.

** Scientific references:

- E. Luján, J. A. Zuloaga Mellino, A. Otero, L. Rey Vega, C. Galarza, E. Mocskos. “NB-IoT: extreme-coverage resource optimization through uplink scheduling”. IEEE Internet of Things Journal. 2019.
- E. Luján, A. Otero, S. Valenzuela, E. Mocskos, L. A. Steffenel and S. Nesmachnow. “An integrated platform for smart energy management: the CC-SEM project”. Revista Facultad de Ingenieria. Universidad de Antioquia. 2019.
- J. A. Zuloaga Mellino, E. Luján, A. Otero, E. Mocskos, L. Rey Vega, C. Galarza. “Lite NB-IoT Simulator for Uplink Layer”. XVIII Workshop on Information Processing and Control. Argentina. 2019.
- E. Luján, A. Otero, S. Valenzuela, E. Mocskos, L. A. Steffenel and S. Nesmachnow. “Cloud Computing for Smart Energy Management (CC-SEM project)”. Communications in Computer and Information Science. Springer. Congreso Iberoamericano de Ciudades Inteligentes (ICSC-CITIES 2018). Soria, España. 2018.


** Requirements:
- python 2.7
- MATLAB 2017b Engine API for Python

** Running:

```
cd "<matlabroot>/extern/engines/python"
sudo python setup.py install
python stepper.py 
```

** Output:
- Stepper.py will create a table `BLERSIMU` within the sqlite3 file `test.db`, containing the following columns:
```
`imcs`, `iru`, `irep`, `isnr`, `finished`, `bler`, `snr`, `tbs`, `totru`
``` 

** In order to monitor simulation state open a new terminal and type:

```
python monitor.py 
```





