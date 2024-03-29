using System;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        // Indirizzo IP e porta del server
        string serverIp = "127.0.0.1";
        int serverPort = 5005;

        // Crea un socket TCP/IP
        using (var clientSocket = new TcpClient())
        {
            // Connessione al server in modo non bloccante
            await clientSocket.ConnectAsync(serverIp, serverPort);

            // Ricevi dati dal server
            byte[] buffer = new byte[1024];
            int bytesRead = await clientSocket.GetStream().ReadAsync(buffer, 0, buffer.Length);

            // Decodifica i dati ricevuti
            string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);

            // Stampa i dati ricevuti
            Console.WriteLine($"Dati ricevuti: {message}");
        }
    }
}