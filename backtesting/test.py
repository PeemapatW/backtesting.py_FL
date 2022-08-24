from strategy import *
from util import *
import tkinter as tk
from tkinter import ttk

SET50_name = [ticker+'.BK' for ticker in ['AOT','PTT','PTTEP','ADVANC','GULF','CPALL','SCC','BDMS','KBANK','SCB','OR','EA','CPN','IVL','BBL','SCGP','CPF','INTUCH','KTB','CRC','PTTGC','GPSC',
 'MINT','HMPRO','AWC','TRUE','KTC','BH','BEM','TTB','BTS','JMT','CBG','DTAC','TOP','OSP','LH','EGCO','BGRIM','MTC','GLOBAL','BANPU','TU','TIDLOR',
 'JMART','KCE','TISCO','BLA','SAWAD','IRPC']]
TopCrypto_name = [ticker+'-USD' for ticker in ['BTC','ETH','BNB','XRP','ADA','SOL','DOGE','HEX','DOT','SHIB','WTRX','MATIC','AVAX','TRX','STETH','WBTC','ETC','UNI1','LEO','YOUC','LTC','FTT','LINK','CRO','NEAR','ATOM','XMR','XLM','BCH','FLOW','ALGO','VET','FIL','ICP',
                  'APE3','MANA','EOS','SAND','HBAR','XTZ','TONCOIN','QNT','WBNB','EGLD','THETA','AAVE','CHZ','AXS','OKB','BSV']]
Asset_name = SET50_name + TopCrypto_name

from tkinter import *
#Create an instance of Tkinter frame or window
win= Tk()
#Set the geometry of tkinter frame
win.geometry("750x350")
#Create ListBoxes
listboxA=Listbox(win, exportselection=False) #Create listboxA
listboxA.pack(padx=10,pady=10,fill=BOTH,expand=True)
listboxB=Listbox(win,exportselection=False) #Create ListboxB
listboxB.pack(padx=10,pady=10,fill=BOTH,expand=True)
listboxA.insert(1, "SMA")
listboxA.insert(2, "MACD")
listboxB.insert(1, "KTC.BK")
listboxB.insert(2, "KBANK.BK")


strategy_dict = {'SMA':SMA_Cross,'MACD':MACD_Cross,'EMA':EMA_Cross,'TRIMA':TRIMA_Cross}
for i,keys in enumerate(list(strategy_dict.keys())):
  listboxA.insert(i, keys)
for i,asset in enumerate(Asset_name):
  listboxB.insert(i, asset)


# handle event
def items_selected(event):
    """ handle item selected event
    """
    # get selected indices
    selected_indicesA = listboxA.curselection()
    selected_indicesB = listboxB.curselection()
    # get selected items
    selected_A = ",".join([listboxA.get(i) for i in selected_indicesA])
    selected_B = ",".join([listboxB.get(i) for i in selected_indicesB])
    Test_Strategy(selected_B,strategy_dict[selected_A],start_date='01/01/20',end_date='08/19/22')

listboxB.bind('<<ListboxSelect>>', items_selected)
win.mainloop()