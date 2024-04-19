
# Definisci il foglio di stile CSS per i pulsanti
gui_style = """
QPushButton {
    background-color: #4CAF50; /* Colore di sfondo */
    border: none; /* Nessun bordo */
    color: white; /* Colore del testo */
    padding: 15px 32px; /* Spazio interno */
    text-align: center; /* Allineamento del testo */
    text-decoration: none; /* Nessuna decorazione del testo */
    font-size: 24px; /* Dimensione del carattere */
    margin: 4px 2px; /* Margine esterno */
    border-radius: 10px; /* Bordi arrotondati */
}
QPushButton:hover {
    background-color: #45a049; /* Cambia colore al passaggio del mouse */
}
QPushButton:pressed {
    background-color: #4CAF50; /* Cambia colore al clic */
}

QLabel {
    font-size: 48px;           /* Dimensione del carattere */
    text-align: center;        /* Allineamento del testo */
}

MainWindow {
    background-color: white;
}



"""