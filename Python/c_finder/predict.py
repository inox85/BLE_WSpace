import csv
import pandas as pd

data = []

df = pd.DataFrame()
df['datetime'] = [0] * len(df)

csv_file = open('log.csv')
csv_reader = csv.reader(csv_file, delimiter=';')

for row in csv_reader:
    colonne_da_aggiungere = [col for col in row[2:] if col not in df.columns]
    nuovo_df = pd.DataFrame({colonna: [0] * len(df) for colonna in colonne_da_aggiungere})
    df = pd.concat([df, nuovo_df], axis=1)

csv_file.seek(0)

for row in csv_reader:
    df.loc[len(df)] = 0
    df.loc[len(df)-1, "datetime"] = row[0]
    for address in row[:2]:
        df.loc[len(df)-1, address] = int(1)  # Inizializza tutti i valori della nuova riga a 0
        

    # Stampa il DataFrame con la nuova riga popolata


print(df)
df.to_csv('dataframe.csv', index=False, sep=';')

