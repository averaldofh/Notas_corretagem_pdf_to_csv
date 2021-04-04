import pandas as pd
import camelot
import datetime as dt
import numpy as np
from os import chdir, listdir
import locale
from PyPDF2 import PdfFileReader
locale.setlocale(locale.LC_ALL, '')

#Areas nrOrdem: ['405,805,475,775'] Data:  ['500,800,575,765'] operações: ['80,575,580,375']  colunas = ['110,165,207,280,352,390,435,553] resumo: ['295,375,580,135]
#folder = r'D:\Python\Notas-de-Corretagem-Clear-pdf-to-pandas-main'
#path_pdf = r'D:\Python\Notas-de-Corretagem-Clear-pdf-to-pandas-main\nota.pdf'
#path_pdf2 = r'D:\Python\Notas-de-Corretagem-Clear-pdf-to-pandas-main\nota2.pdf'
path = r'D:\Python\Notas-de-Corretagem-Clear-pdf-to-pandas-main'
global p
global m
Lista_empresas = pd.read_excel(r'D:\Python\Notas-de-Corretagem-Clear-pdf-to-pandas-main\Empresas_Listadas.xlsx')

def ticker(df):
    for i in np.arange(len(df)):
        y = df.loc[df.index[i], 'TICKER']
        cod = ''
        for j in np.arange(len(Lista_empresas)):
            if y in Lista_empresas['Nome de Pregão'][j]:
                cod = str(Lista_empresas['Código'][j])[:5]
                df.at[i,'TICKER'] = cod
    return df

def lenota(path):
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

        notas = notas.append(opr, sort=False, ignore_index=True)
        for index, row in opr.iterrows():
            notas.at[index,7] = locale.format('%.2f', ((locale.atof(row[6]))/total * tx))
        notas.rename(columns={0:'DATA',1:'Nr NOTA',2:'C/V',3:'TICKER',4:'QTD',5:'PM',6:'VALOR',7:'TX PROP'}, inplace=True)
        notas = ticker(notas)
        notas.to_clipboard(excel=True, sep=',', index=False)
        return 1
    else:
        return 0
        
def lepasta(path):
    arquivos_path = listdir(path)
    notas_path = []
    for i in range(len(arquivos_path)):
                if ('Nota' in arquivos_path[i] or 'nota' in arquivos_path[i]) and 'pdf' in arquivos_path[i]:
                    notas_path.append(arquivos_path[i])
    
    output = pd.DataFrame()
    p=0
    m = len(notas_path)
    for j in notas_path:
        p += 1
        pgchk = r'{}\{}'.format(path,j)
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
                opr.at[index,7] = locale.format('%.2f', ((locale.atof(row[6]))/total * tx))
                if opr.at[index,2]=='V':
                    opr.at[index,6] = '-'+opr.at[index,6]
            output = output.append(opr, sort=False, ignore_index=True)
    output.rename(columns={0:'DATA',1:'Nr NOTA',2:'C/V',3:'TICKER',4:'QTD',5:'PM',6:'VALOR',7:'TX PROP'}, inplace=True)
    output = ticker(output)
    output.to_csv(path+r'\Notas.csv', sep=',', na_rep='erro', index=False)
    return 1
