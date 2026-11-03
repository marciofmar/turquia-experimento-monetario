"""Universo fixado antes do ajuste; sem seleção pelo pós-tratamento."""
COUNTRIES={'TUR':'Turquia','BRA':'Brasil','POL':'Polônia','HUN':'Hungria','CZE':'Tchéquia','ROU':'Romênia','SRB':'Sérvia','ZAF':'África do Sul','CHL':'Chile','MEX':'México','MYS':'Malásia','THA':'Tailândia','COL':'Colômbia','IND':'Índia','NGA':'Nigéria','EGY':'Egito','GHA':'Gana'}
PRINCIPAL=['MEX','POL','BRA','ZAF','MYS','THA','ROU','HUN','COL','CHL','IND','CZE','SRB']
POOLS={'principal':PRINCIPAL,'extended':PRINCIPAL+['NGA','EGY','GHA']}
LEGACY_POOLS={'all':['BRA','POL','HUN','CZE','ROU','SRB','ZAF','CHL','NGA','EGY','GHA'],'europe':['POL','HUN','CZE','ROU','SRB'],'emerging':['BRA','CHL','ZAF','NGA','EGY','GHA']}
COVARIATES=['income_ppp','investment','openness','manufacturing']
START_YEAR=2010
END_YEAR=2026
INDICATORS={
 'gdp':('NY.GDP.MKTP.KD.ZG','Crescimento real do PIB','% ao ano'),
 'inflation':('FP.CPI.TOTL.ZG','Inflação ao consumidor','% · média anual'),
 'fx':('PA.NUS.FCRF','Câmbio oficial','moeda local por US$ · média anual'),
 'current':('BN.CAB.XOKA.GD.ZS','Conta corrente','% do PIB'),
 'productivity':('SL.GDP.PCAP.EM.KD','PIB por pessoa empregada','US$ PPC constantes de 2021'),
 'investment':('NE.GDI.FTOT.ZS','Formação bruta de capital fixo','% do PIB'),
 'hightech':('TX.VAL.TECH.MF.ZS','Exportações de alta tecnologia','% das exportações de manufaturados'),
 'manufacturing':('NV.IND.MANF.ZS','Valor adicionado da indústria de transformação','% do PIB'),
 'rd':('GB.XPD.RSDV.GD.ZS','Pesquisa e desenvolvimento','% do PIB'),
 'income':('NY.GDP.PCAP.KD','PIB real por habitante','US$ constantes de 2015'),
 'income_ppp':('NY.GDP.PCAP.PP.KD','PIB por habitante em PPC','US$ PPC constantes de 2021'),
 'openness':('NE.TRD.GNFS.ZS','Abertura comercial (exportações + importações)','% do PIB'),
 'exports':('NE.EXP.GNFS.ZS','Exportações de bens e serviços','% do PIB')}
ISO2={'TR':'TUR','BR':'BRA','PL':'POL','HU':'HUN','CZ':'CZE','RO':'ROU','RS':'SRB','ZA':'ZAF','CL':'CHL','MX':'MEX','MY':'MYS','TH':'THA','CO':'COL','IN':'IND','NG':'NGA','EG':'EGY','GH':'GHA'}
