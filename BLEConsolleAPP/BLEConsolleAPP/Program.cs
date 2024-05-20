using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        // Indirizzo IP e porta del server
        string serverIp = "192.168.13.52";
        int serverPort = 5005;

        // Crea un socket TCP/IP

            // Connessione al server in modo non bloccante
        while (true)
        {
            try
            {
                using (var clientSocket = new TcpClient())
                {
                    await clientSocket.ConnectAsync(serverIp, serverPort);

                    // Ricevi dati dal server

                    byte[] buffer = new byte[1024];
                    int bytesRead = await clientSocket.GetStream().ReadAsync(buffer, 0, buffer.Length);

                    // Decodifica i dati ricevuti
                    string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);

                    // Stampa i dati ricevuti
                    Console.WriteLine($"Dati ricevuti: {message}");
                    Thread.Sleep(1000);
                }
            }
            catch (Exception ex) 
            {
                Console.WriteLine($"Impossibile raggiungere il server {ex}");
            }
        }
    }
}