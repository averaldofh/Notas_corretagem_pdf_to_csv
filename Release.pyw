import tkinter as tk
import tkinter.ttk as ttk
import os
import pandas as pd
import camelot
import datetime as dt
import numpy as np
import locale
from PyPDF2 import PdfFileReader
locale.setlocale(locale.LC_ALL, '')
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import webbrowser
import sys
# sys.stdout = open(os.devnull, "w")
# sys.stderr = open(os.devnull, "w")

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def callback(url):
    webbrowser.open_new(url)

def ticker(df):
    global Lista_empresas
    for i in np.arange(len(df)):
        y = df.loc[df.index[i], 'TICKER']
        cod = ''
        for j in np.arange(len(Lista_empresas)):
            if y in Lista_empresas['Nome de Pregão'][j]:
                cod = str(Lista_empresas['Código'][j])[:5]
                df.at[i,'TICKER'] = cod
    return df

def lenota(path):
    global p,m
    pg = PdfFileReader(open(path,'rb')).getNumPages()
    if pg == 1:
        del pg
        notas = pd.DataFrame()#(columns=['DATA','NOTA','C/V','TICKER','QTD','PM','VALOR','TAXA PROP','IRRF'])
        tables = camelot.read_pdf(path, flavor='stream', table_areas = ['80,560,560,370','520,785,570,775','425,785,470,775','300,350,555,135'],columns=['110,165,278,352,435,485','','',''])
        nrNota = tables[1].df[0][0]
        date = tables[0].df
        data = dt.datetime.strptime(date[6][0], '%d/%m/%Y').date()
        data = data.strftime('%d/%m/%Y')
        del date

        tx = locale.atof(tables[3].df[2][2]) + locale.atof(tables[3].df[2][8])
        total = locale.atof(tables[3].df[2][1])

        opr = tables[2].df
        opr.drop(opr.columns[[1,2]], axis=1, inplace=True)
        opr.insert(0,'a',nrNota)
        opr.insert(0,'b',data)
        del data, nrNota
        opr.columns = range(opr.shape[1])
        m = opr.shape[0]
        notas = notas.append(opr, sort=False, ignore_index=True)
        for index, row in opr.iterrows():
            p = index+1
            notas.at[index,7] = locale.format('%.2f', ((locale.atof(row[6]))/total * tx))
        notas.rename(columns={0:'DATA',1:'Nr NOTA',2:'C/V',3:'TICKER',4:'QTD',5:'PM',6:'VALOR',7:'TX PROP'}, inplace=True)
        notas = ticker(notas)
        notas.to_clipboard(excel=True, sep=',', index=False)
        return 1
    else:
        return 0

def lepasta(path):
    global p, m, error
    arquivos_path = os.listdir(path)
    notas_path = []
    for i in range(len(arquivos_path)):
                if ('Nota' in arquivos_path[i] or 'nota' in arquivos_path[i]) and 'pdf' in arquivos_path[i]:
                    notas_path.append(arquivos_path[i])
    
    output = pd.DataFrame()
    p=0
    m = len(notas_path)
    for j in notas_path:
        p += 1
        NotasApp.upd_progress(app)
        pgchk = r'{}\{}'.format(resource_path(path),j)
        pg = PdfFileReader(open(pgchk,'rb')).getNumPages()
        if pg <= 1:
            path_pdf = (r'{}\{}'.format(path, j))
            #print ('Arquivo: ', j)
            tables = camelot.read_pdf(path_pdf, flavor='stream', table_areas = ['80,560,560,370','520,785,570,775','425,785,470,775','300,350,555,135'],columns=['110,165,278,352,435,485','','',''])
            nrNota = tables[1].df[0][0]
            #print ('nr. nota: ', nrNota)
            date = tables[0].df
            data = dt.datetime.strptime(date[6][0], '%d/%m/%Y').date()
            data = data.strftime('%d/%m/%Y')
            #print ('data: ', data)
            tx = locale.atof(tables[3].df[2][2]) + locale.atof(tables[3].df[2][8])
            #print ('Taxas: ', tx)
            total = locale.atof(tables[3].df[2][1])
            #print ('Total da nota: ', total, '\n')
            del date
            opr = tables[2].df
            del tables
            opr.drop(opr.columns[[1,2]], axis=1, inplace=True)
            opr.insert(0,'a',nrNota)
            opr.insert(0,'b',data)
            del data, nrNota
            opr.columns = range(opr.shape[1])
            for index, row in opr.iterrows():
                opr.at[index,7] = locale.format_string('%.2f', ((locale.atof(row[6]))/total * tx))
            output = output.append(opr, sort=False, ignore_index=True)
        else:
            error = 1
    output.rename(columns={0:'DATA',1:'Nr NOTA',2:'C/V',3:'TICKER',4:'QTD',5:'PM',6:'VALOR',7:'TX PROP'}, inplace=True)
    output = ticker(output)
    output.to_csv(path+r'\Notas.csv', sep=',', na_rep='erro', index=False)
    return 1

class NotasApp:
    def __init__(self, master=None):
        # build ui
        self.mainWindow = tk.Tk() if master is None else tk.Toplevel(master)
        self.fr_main = ttk.Frame(self.mainWindow)
        self.frame6 = ttk.Frame(self.fr_main)
        self.lbl_title = ttk.Label(self.frame6)
        self.lbl_title.configure(font='{Calibri} 16 {}', text='Importador de notas PDF V0.1')
        self.lbl_title.pack(side='top')
        self.lbl_git = ttk.Label(self.frame6)
        self.lbl_git.configure(cursor='hand2', font='{calibri} 12 {underline}', foreground='#0000ff', text='github.com')
        self.lbl_git.pack(side='top')
        self.lbl_git.bind('<1>', lambda e: callback("http://www.github.com/averaldofh"))
        self.frame6.configure(height='50', width='500')
        self.frame6.pack(fill='x', side='top')
        self.frame6.pack_propagate(0)
        self.fr_singleFile = ttk.Labelframe(self.fr_main)
        self.btn_fileopen = ttk.Button(self.fr_singleFile)
        self.btn_fileopen.configure(text='Abrir PDF...')
        self.btn_fileopen.pack(anchor='n', side='left')
        self.btn_fileopen.pack_propagate(0)
        self.btn_fileopen.configure(command=self.cmd_filesel)
        self.ent_filepath = ttk.Entry(self.fr_singleFile)
        _text_ = '''Selecione o PDF para exportar o conteúdo para a área de transferência...'''
        self.ent_filepath.delete('0', 'end')
        self.ent_filepath.insert('0', _text_)
        self.ent_filepath.pack(anchor='n', expand='true', fill='x', ipady='2', side='left')
        self.ent_filepath.pack_propagate(0)
        self.btn_procfile = ttk.Button(self.fr_singleFile)
        self.btn_procfile.configure(default='disabled', state='disabled', text='Copiar para área de transferência')
        self.btn_procfile.place(anchor='center', relx='0.5', rely='0.7', x='0', y='0')
        self.btn_procfile.configure(command=self.cmd_file)
        self.fr_singleFile.configure(height='80', text='Arquivo Único', width='200')
        self.fr_singleFile.pack(fill='x', side='top')
        self.fr_singleFile.pack_propagate(0)
        self.fr_folder = ttk.Labelframe(self.fr_main)
        self.btn_folderSel = ttk.Button(self.fr_folder)
        self.btn_folderSel.configure(text='Abrir pasta...')
        self.btn_folderSel.pack(anchor='n', side='left')
        self.btn_folderSel.configure(command=self.cmd_folder)
        self.ent_folderPath = ttk.Entry(self.fr_folder)
        self.ent_folderPath.configure(font='TkDefaultFont')
        _text_ = '''Selecione a pasta para exportar todas as notas em um arquivo CSV...'''
        self.ent_folderPath.delete('0', 'end')
        self.ent_folderPath.insert('0', _text_)
        self.ent_folderPath.pack(anchor='n', expand='true', fill='x', ipady='2', side='left')
        self.btn_procFolder = ttk.Button(self.fr_folder)
        self.btn_procFolder.configure(default='disabled', state='disabled', text='Gerar CSV')
        self.btn_procFolder.place(anchor='center', relx='0.4', rely='0.70', x='0', y='0')
        self.btn_procFolder.configure(command=self.cmd_foldercsv)
        self.btn_opencsv = ttk.Button(self.fr_folder)
        self.btn_opencsv.configure(default='disabled', state='disabled', text='Abrir CSV')
        self.btn_opencsv.place(anchor='center', relx='0.6', rely='0.7', x='0', y='0')
        self.btn_opencsv.configure(command=self.cmd_opencsv)
        self.fr_folder.configure(height='80', text='Múltiplos Arquivos', width='200')
        self.fr_folder.pack(fill='x', side='top')
        self.fr_folder.pack_propagate(0)
        self.fr_pb = ttk.Frame(self.fr_main)
        self.progressbar1 = ttk.Progressbar(self.fr_pb)
        self.progressbar1.configure(orient='horizontal')
        self.progressbar1.pack(expand='true', fill='x', side='left')
        self.lbl_counter = ttk.Label(self.fr_pb)
        self.lbl_counter.configure(text='0 / 0')
        self.lbl_counter.pack(anchor='center', side='left')
        self.fr_pb.configure(height='60', width='480')
        self.fr_pb.pack(side='top')
        self.fr_pb.pack_propagate(0)
        self.fr_footer = ttk.Frame(self.fr_main)
        self.lbl_averaldo = ttk.Label(self.fr_footer)
        self.lbl_averaldo.configure(text='@averaldofh')
        self.lbl_averaldo.pack(anchor='s', side='left')
        self.btn_quit = ttk.Button(self.fr_footer)
        self.btn_quit.configure(text='Sair')
        self.btn_quit.pack(anchor='s', side='right')
        self.btn_quit.configure(command=self.cmd_close)
        self.fr_footer.configure(height='25', width='500')
        self.fr_footer.pack(side='bottom')
        self.fr_footer.pack_propagate(0)
        self.fr_main.configure(height='300', width='500')
        self.fr_main.pack(side='top')
        self.fr_main.pack_propagate(0)
        self.mainWindow.geometry('500x300')
        self.mainWindow.resizable(False, False)
        self.mainWindow.title('Importador de Notas')

        # Main widget
        self.mainwindow = self.mainWindow
    
    def cmd_filesel(self):
        file = askopenfilename()
        self.ent_filepath.delete('0','end')
        self.ent_filepath.insert('0',file)
        self.btn_procfile['state'] = tk.NORMAL
        pass

    def cmd_file(self):
        file = self.ent_filepath.get()
        if (lenota(file)):
            self.ent_filepath.delete('0','end')
            self.ent_filepath.insert('0','Tabela copiada para a área de transferência!!')
            self.btn_procfile['state'] = tk.DISABLED
        else:
            self.ent_filepath.delete('0','end')
            self.ent_filepath.insert('0','ERRO AO PROCESSAR ARQUIVO')
            self.btn_procfile['state'] = tk.DISABLED
        pass

    def cmd_folder(self):
        global generalstr
        pathin = generalstr = askdirectory()
        m = len(os.listdir(pathin))
        pg = f'0 / {m}'
        self.lbl_counter['text'] = pg
        generalstr = pathin + r'\Notas.csv'
        self.ent_folderPath.delete('0','end')
        self.ent_folderPath.insert('0',pathin)
        self.btn_procFolder['state'] = tk.NORMAL
        pass

    def cmd_foldercsv(self):
        global error
        pathin = self.ent_folderPath.get()
        lepasta(pathin)
        if error==1:
            self.ent_folderPath.delete('0','end')
            self.ent_folderPath.insert('0','ERRO AO PROCESSAR UM OU MAIS ARQUIVOS')
            self.btn_procFolder['state'] = tk.DISABLED
            self.btn_opencsv['state'] = tk.NORMAL
        else:
            self.ent_folderPath.delete('0','end')
            self.ent_folderPath.insert('0','Tabela salva na pasta de origem!!')
            self.btn_procFolder['state'] = tk.DISABLED
            self.btn_opencsv['state'] = tk.NORMAL

    def cmd_opencsv(self):
        global generalstr
        csvfile = '"{}"'.format(generalstr)
        os.system(csvfile)


    def cmd_close(self):
        self.mainWindow.quit()

    def upd_progress(self):
        global m, p
        pg = f'{p} / {m}'
        self.progressbar1['maximum'] = m
        self.progressbar1['value'] = p
        self.lbl_counter['text'] = pg
        self.mainWindow.update()

    def run(self):
        self.mainwindow.mainloop()

if __name__ == '__main__':
    import tkinter as tk
    import tkinter.ttk as ttk
    import pandas as pd
    generalstr = ''
    p,m,error = 0,0,0
    tickpath = resource_path(r'Empresas_Listadas.xls')
    Lista_empresas = pd.read_excel(tickpath)
    app = NotasApp()
    app.run()

