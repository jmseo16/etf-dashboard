# rx_s1 block-level drawing model (shared by HTML/PPTX generator and checker)
# groups map top-level instances of dq_rx_unit to drawn nodes
GROUPS = {
 'PAD':  ['xi20','xi21'],
 'DEC':  ['xi22'],
 'BIAS': ['xi23'],
 'PRE':  ['xi24','r0','mn0','xi0','xi1','xi2','xi3','xi4'],
 'SGN':  ['xi5','xi6'],
 'CKG':  ['xi25'],
 'SUM_E':['xi26'], 'SUM_O':['xi27'],
 'SA_E': ['xi28'], 'SA_O':['xi29'],
 'SR_E': ['xi30'], 'SR_O':['xi31'],
 'OUT_E':['xi7','xi8','xi9'], 'OUT_O':['xi10','xi11','xi12'],
}
HIDDEN_NODES = {'BIAS'}
HIDDEN_PORTS = {'ibias','ofe_p<1>','ofe_p<0>','ofe_n<1>','ofe_n<0>','ofo_p<1>','ofo_p<0>','ofo_n<1>','ofo_n<0>','vdd','vddq','vss','vssq'}
BUS_OF = {'tap<3>':'tap<3:0>','tap<2>':'tap<3:0>','tap<1>':'tap<3:0>','tap<0>':'tap<3:0>',
          'rtt<2>':'rtt<2:0>','rtt<1>':'rtt<2:0>','rtt<0>':'rtt<2:0>'}
PORTS = ['pad','vref','ck','ckb','lb_p','lb_n','lb_en','rx_en','odt_en','rtt<2:0>','tap<3:0>','tap_sgn','dout_e','dout_o']

BOXES = {
 'PAD':  dict(x=150,y=85,w=150,h=80,title='PAD 종단·ESD',sub='ESD 다이오드·직렬 R·ODT'),
 'DEC':  dict(x=150,y=195,w=150,h=50,title='DEC',sub='ODT 디코더 (K4)'),
 'PRE':  dict(x=340,y=220,w=170,h=170,title='PRE (입력 선택)',sub='입력쌍 2 · 부하 R · 상보 선택'),
 'SGN':  dict(x=330,y=600,w=120,h=40,title='SGN',sub='극성 INV 2개'),
 'CKG':  dict(x=150,y=470,w=150,h=50,title='CK 게이트',sub='NAND·INV (클럭 게이트)'),
 'SUM_E':dict(x=610,y=100,w=110,h=60,title='SUM',sub='DFE 합산 (짝)'),
 'SA_E': dict(x=745,y=100,w=110,h=60,title='비교기',sub='StrongARM (짝)'),
 'SR_E': dict(x=880,y=100,w=100,h=60,title='SR 래치',sub='(짝)'),
 'SUM_O':dict(x=610,y=460,w=110,h=60,title='SUM',sub='DFE 합산 (홀)'),
 'SA_O': dict(x=745,y=460,w=110,h=60,title='비교기',sub='StrongARM (홀)'),
 'SR_O': dict(x=880,y=460,w=100,h=60,title='SR 래치',sub='(홀)'),
 'OUT_E':dict(x=1040,y=100,w=80,h=60,title='버퍼',sub='INV·INV'),
 'OUT_O':dict(x=1040,y=460,w=80,h=60,title='버퍼',sub='INV·INV'),
}
FRAMES = [dict(x=595,y=65,w=540,h=130,title='DFE 슬라이스 (짝수)'),
          dict(x=595,y=425,w=540,h=130,title='DFE 슬라이스 (홀수)')]
PORT_POS = {'pad':(30,125),'odt_en':(30,205),'rtt<2:0>':(30,240),'vref':(30,290),'lb_p':(30,320),
            'lb_n':(30,340),'lb_en':(30,380),'rx_en':(30,400),'ck':(30,480),'ckb':(30,505),
            'tap_sgn':(30,620),'tap<3:0>':(660,30),'dout_e':(1150,130),'dout_o':(1150,490)}
N = lambda *a: list(a)
EDGES = [
 ('P:pad','PAD',['pad']),
 ('PAD','PRE',['net1']),
 ('P:odt_en','DEC',['odt_en']),
 ('P:rtt<2:0>','DEC',['rtt<2>','rtt<1>','rtt<0>']),
 ('DEC','PAD',['net2<2>','net2<1>','net2<0>']),
 ('P:vref','PRE',['vref']),
 ('P:lb_p','PRE',['lb_p']),
 ('P:lb_n','PRE',['lb_n']),
 ('P:lb_en','PRE',['lb_en']),
 ('P:rx_en','PRE',['rx_en']),
 ('PRE','SUM_E',['net6','net7']),
 ('PRE','SUM_O',['net6','net7']),
 ('SUM_E','SA_E',['net10','net11']),
 ('SUM_O','SA_O',['net12','net13']),
 ('SA_E','SR_E',['net18','net19']),
 ('SA_O','SR_O',['net24','net25']),
 ('SR_E','SUM_O',['net14','net15']),
 ('SR_O','SUM_E',['net16','net17']),
 ('SR_E','OUT_E',['net14','net15']),
 ('SR_O','OUT_O',['net16','net17']),
 ('OUT_E','P:dout_e',['dout_e']),
 ('OUT_O','P:dout_o',['dout_o']),
 ('P:ck','CKG',['ck']),
 ('P:ckb','CKG',['ckb']),
 ('P:rx_en','CKG',['rx_en']),
 ('CKG','SA_E',['net8']),
 ('CKG','SA_O',['net9']),
 ('P:tap_sgn','SGN',['tap_sgn']),
 ('SGN','SUM_E',['net105','net106']),
 ('SGN','SUM_O',['net105','net106']),
 ('P:tap<3:0>','SUM_E',['tap<3>','tap<2>','tap<1>','tap<0>']),
 ('P:tap<3:0>','SUM_O',['tap<3>','tap<2>','tap<1>','tap<0>']),
 ('P:rx_en','SUM_E',['rx_en']),
 ('P:rx_en','SUM_O',['rx_en']),
]
