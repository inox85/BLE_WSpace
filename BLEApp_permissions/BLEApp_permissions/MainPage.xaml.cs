using Android.Bluetooth.LE;
using Android.Util;
using Java.Nio.Channels;
using Plugin.BLE;
using Plugin.BLE.Abstractions.Contracts;
using Plugin.BLE.Abstractions.EventArgs;
using System.Collections.ObjectModel;
using System.Text;
using static Microsoft.Maui.ApplicationModel.Permissions;



namespace BLEApp_permissions
{

   
    public partial class MainPage : ContentPage
    {
        public string SelectedOption { get; set; } = "Spento";


        private readonly IBluetoothLE ble;
        private readonly IAdapter adapter;
        private bool scanning = false;

        List<string> items = new List<string>();
        IDevice connectedDevice;



        public MainPage(DeviceItem selectedDevice)
        {
            InitializeComponent();

            ble = CrossBluetoothLE.Current;
            adapter = CrossBluetoothLE.Current.Adapter;

            var customServiceServiceUUID = Guid.NewGuid();      

            var customServiceCustomUUID = Guid.NewGuid();

            BindingContext = this;

            //lstDevices.ItemsSource = devicesList;
            //myListView.ItemsSource = items;
        }




        private async void OnScanButtonClicked(object sender, EventArgs e)
        {
            try
            {

                var statusBle = await Permissions.CheckStatusAsync<Platforms.Android.BluetoothPermissions>();
                var statusLocation = await Permissions.CheckStatusAsync<Platforms.Android.BluetoothPermissions>();

                if (statusBle != PermissionStatus.Granted)
                {
                    statusBle = await Permissions.RequestAsync<Platforms.Android.BluetoothPermissions>();
                }

                if (statusBle != PermissionStatus.Granted)
                {
                    // Gestire il caso in cui l'utente non abbia concesso il permesso
                }
                else
                {
                    // Permesso concesso, avvia la scansione Bluetooth
                    //await StartBluetoothScan();
                    //StartScan();

                    scanning = true;
                    //lblStatus.Text = "Scanning...";
                    adapter.DeviceDiscovered += OnDeviceDiscovered;
                    adapter.ScanTimeout = 20000;
                    await adapter.StartScanningForDevicesAsync();
                }
            }
            catch (Exception ex)
            {
                // Gestire eventuali eccezioni
            }

            
        }

        //private async Task StartScan()
        //{
        //    //scanning = true;
        //    ////lblStatus.Text = "Scanning...";
        //    //var devices = await adapter.StartScanningForDevicesAsync();

        //    //// Handle the discovered devices
        //    //HandleDiscoveredDevices(devices);

        //    scanning = true;
        //    //lblStatus.Text = "Scanning...";
        //    adapter.DeviceDiscovered += OnDeviceDiscovered;
        //    adapter.ScanTimeout = 20000;
        //    await adapter.StartScanningForDevicesAsync();
        //}

        List<IDevice> foundDevices = new List<IDevice>();

        private void OnDeviceDiscovered(object sender, DeviceEventArgs e)
        {
            //throw new NotImplementedException();
            var device = e.Device;
            Console.WriteLine($"Dispositivo trovato: {device.Name}, ID: {device.Id}, Address: {device.NativeDevice}");
            ///AddDeviceToList($"Dispositivo trovato: {device.Name}, ID: {device.Id}, Address: {device.NativeDevice}");
            //scanBtn.Text = $"Dispositivo trovato: {device.Name}, ID: {device.Id}, Address: {device.NativeDevice}";
            items.Add($"Dispositivo trovato: {device.Name}, Address: {device.NativeDevice}");
            //myListView.ItemsSource = null;
            //myListView.ItemsSource = items;

            //ConnectAndDiscoverServices(device);
            foundDevices.Add(device);


            if (device.NativeDevice.ToString().Contains("85:EA") || device.NativeDevice.ToString().Contains("F6:FE"))
            {
                //ConnectAndDiscoverServices(device);
                //ConnectAndDiscoverServices(device);

                //ConnectAndSubscribeToCharacteristic(device, new Guid("19B10001-E8F2-537E-4F6C-D104768A1214"), new Guid("19B10003-E8F2-537E-4F6C-D104768A1214"));
                //ConnectAndSubscribeToCharacteristic(device, new Guid("19B10000-E8F2-537E-4F6C-D104768A1214"), new Guid("19B10002-E8F2-537E-4F6C-D104768A1214"));
                
                connectedDevice = device;
                ConnectAndSubscribeToMultipleCharacteristics(device);
            }



        }


        private async Task StopScan()
        {
            scanning = false;
            //lblStatus.Text = "Scan Stopped";
            await adapter.StopScanningForDevicesAsync();
        }

        private async void ConnectAndDiscoverServices(List<IDevice> devices)
        {
            foreach (var device in devices)
            {
                try
                {
                    // Connessione al dispositivo
                    await adapter.ConnectToDeviceAsync(device);


                    Thread.Sleep(1000);
                    // Visualizza i servizi del dispositivo
                    var services = await device.GetServicesAsync();
                    foreach (var service in services)
                    {
                        Console.WriteLine($"Servizio: {service.Id}");

                        // Visualizza le caratteristiche del servizio
                        var characteristics = await service.GetCharacteristicsAsync();
                        foreach (var characteristic in characteristics)
                        {
                            Console.WriteLine($"Caratteristica: {characteristic.Id}");
                        }
                    }

                    // Disconnessione dal dispositivo
                    await CrossBluetoothLE.Current.Adapter.DisconnectDeviceAsync(device);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Errore durante la connessione al dispositivo {device.Name}: {ex.Message}");
                }
            }
        }

        private async void ConnectAndDiscoverServices(IDevice device)
        {
            try
            {
                // Connessione al dispositivo
                await CrossBluetoothLE.Current.Adapter.ConnectToDeviceAsync(device);

                // Visualizza i servizi del dispositivo
                var services = await device.GetServicesAsync();
                foreach (var service in services)
                {
                    Console.WriteLine($"Servizio: {service.Id}");

                    // Visualizza le caratteristiche del servizio
                    var characteristics = await service.GetCharacteristicsAsync();
                    foreach (var characteristic in characteristics)
                    {
                        Console.WriteLine($"Caratteristica: {characteristic.Id}");
                    }
                }

                // Disconnessione dal dispositivo
                await CrossBluetoothLE.Current.Adapter.DisconnectDeviceAsync(device);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Errore durante la connessione al dispositivo {device.Name}: {ex.Message}");
            }   
        }

        //private async void ConnectAndSubscribeToCharacteristic(IDevice device, Guid serviceId, Guid characteristicId)
        //{
        //    try
        //    {
        //        // Connessione al dispositivo
        //        await CrossBluetoothLE.Current.Adapter.ConnectToDeviceAsync(device);

        //        // Ottenere il servizio contenente la caratteristica desiderata
        //        //Guid serviceId = new Guid("00001801-0000-1000-8000-00805F9B34FB");

        //        var services = await device.GetServicesAsync();
        //        foreach (var ser in services)
        //        {
        //            Console.WriteLine($"Servizio: {ser.Id}");

        //            // Visualizza le caratteristiche del servizio
        //            var characteristics = await ser.GetCharacteristicsAsync();
        //            foreach (var ch in characteristics)
        //            {
        //                Console.WriteLine($"Caratteristica: {ch.Id}");
        //            }
        //        }

        //        var service = await device.GetServiceAsync(serviceId);

        //        // Ottenere la caratteristica desiderata
        //        var characteristic = await service.GetCharacteristicAsync(characteristicId);

        //        // Sottoscrivi gli aggiornamenti della caratteristica
        //        characteristic.ValueUpdated += Characteristic_ValueUpdated;
        //        await characteristic.StartUpdatesAsync();

        //        // Attendere gli aggiornamenti della caratteristica (questo può essere fatto in un gestore di eventi separato)
        //        // In questo esempio, lo faremo qui, ma in un'applicazione reale, è preferibile farlo in un gestore di eventi dedicato
        //        await Task.Delay(Timeout.Infinite);
        //    }
        //    catch (Exception ex)
        //    {
        //        Console.WriteLine($"Errore durante la connessione al dispositivo {device.Name}: {ex.Message}");
        //    }
        //}

        private async void ConnectAndSubscribeToMultipleCharacteristics(IDevice device)
        {
            try
            {
                // Connessione al dispositivo per il primo servizio
                await adapter.ConnectToDeviceAsync(device);

                scanBtn.Text = "Disconnetti";

                IReadOnlyList<IService> services = await device.GetServicesAsync();

                do
                {
                    services = await device.GetServicesAsync();
                    foreach (var ser in services)
                    {
                        Console.WriteLine($"Servizio: {ser.Id}");

                        // Visualizza le caratteristiche del servizio
                        var characteristics = await ser.GetCharacteristicsAsync();
                        foreach (var ch in characteristics)
                        {
                            Console.WriteLine($"Caratteristica: {ch.Id}");
                        }
                    }
                    
                } while (services.Count < 3);

                Thread.Sleep(1000);

                var service = await device.GetServiceAsync(new Guid("19B10000-E8F2-537E-4F6C-D104768A1214"));
                
                if (service != null)
                {

                    var characteristic1 = await service.GetCharacteristicAsync(new Guid("19B10002-E8F2-537E-4F6C-D104768A1214"));
                    characteristic1.ValueUpdated += Characteristic_BatteryUpdated;

                    var characteristic2 = await service.GetCharacteristicAsync(new Guid("19B10003-E8F2-537E-4F6C-D104768A1214"));
                    characteristic2.ValueUpdated += Characteristic_CustomUpdated;
                                   
                    var characteristic3 = await service.GetCharacteristicAsync(new Guid("19B10007-E8F2-537E-4F6C-D104768A1214"));
                    characteristic3.ValueUpdated += Characteristic_StringUpdated;
                   
                    var characteristic4 = await service.GetCharacteristicAsync(new Guid("19B1000B-E8F2-537E-4F6C-D104768A1214"));
                    characteristic4.ValueUpdated += Characteristic_BooleanUpdated;


                    await characteristic1.StartUpdatesAsync();
                    await characteristic2.StartUpdatesAsync();
                    await characteristic3.StartUpdatesAsync();
                    await characteristic4.StartUpdatesAsync();

                }



                //var service4 = await device.GetServiceAsync(new Guid("19B1000A-E8F2-537E-4F6C-D104768A1214"));

                //if (service4 != null)
                //{
                //    var characteristic = await service4.GetCharacteristicAsync(new Guid("19B1000B-E8F2-537E-4F6C-D104768A1214"));

                //    // Sottoscrivi gli aggiornamenti della caratteristica
                //    characteristic.ValueUpdated += Characteristic_BooleanUpdated;

                //    await characteristic.StartUpdatesAsync();
                //}

                //var service1 = await device.GetServiceAsync(new Guid("19B10000-E8F2-537E-4F6C-D104768A1214"));
                //if (service1 != null)
                //{

                //    // Ottenere la caratteristica desiderata
                //    var characteristic = await service1.GetCharacteristicAsync(new Guid("19B10002-E8F2-537E-4F6C-D104768A1214"));

                //    // Sottoscrivi gli aggiornamenti della caratteristica
                //    characteristic.ValueUpdated += Characteristic_BatteryUpdated;
                //    await characteristic.StartUpdatesAsync();
                //}

                //// Connessione al dispositivo per il secondo servizio
                //await CrossBluetoothLE.Current.Adapter.ConnectToDeviceAsync(device);
                
                //var service2 = await device.GetServiceAsync(new Guid("19B10000-E8F2-537E-4F6C-D104768A1214"));              

                //if (service2 != null)
                //{
                //    var characteristic = await service2.GetCharacteristicAsync(new Guid("19B10003-E8F2-537E-4F6C-D104768A1214"));

                //    // Sottoscrivi gli aggiornamenti della caratteristica
                //    characteristic.ValueUpdated += Characteristic_CustomUpdated;

                //    await characteristic.StartUpdatesAsync();
                //}

                //var service3 = await device.GetServiceAsync(new Guid("19B10006-E8F2-537E-4F6C-D104768A1214"));

                //if (service3 != null)
                //{
                //    var characteristic = await service3.GetCharacteristicAsync(new Guid("19B10007-E8F2-537E-4F6C-D104768A1214"));

                //    // Sottoscrivi gli aggiornamenti della caratteristica
                //    characteristic.ValueUpdated += Characteristic_StringUpdated;

                //    await characteristic.StartUpdatesAsync();
                //}


            }
            catch (Exception ex)
            {
                Console.WriteLine($"Errore durante la connessione al dispositivo {device.Name}: {ex.Message}");
            }
        }

        private void Characteristic_BatteryUpdated(object sender, CharacteristicUpdatedEventArgs e)
        {
            // Esegui azioni per gestire gli aggiornamenti della caratteristica qui
            var characteristic = e.Characteristic;
            var value = characteristic.Value[0]; // Ottieni il valore della caratteristica
            Console.WriteLine($"Valore aggiornato della batteria: {value}");

            MainThread.BeginInvokeOnMainThread(() =>
            {
                lblBattery.Text = $"Torbidità: {value}";
            });
        }

        private void Characteristic_BooleanUpdated(object sender, CharacteristicUpdatedEventArgs e)
        {            // Esegui azioni per gestire gli aggiornamenti della caratteristica qui
            var characteristic = e.Characteristic;
            var value = characteristic.Value[0]; // Ottieni il valore della caratteristica
            Console.WriteLine($"Valore aggiornato della caratteristica booleana: {value}");

            MainThread.BeginInvokeOnMainThread(() =>
            {
                lblBoolean.Text = $"Laser acceso: {value}";
            });
        }


        // Gestisce gli aggiornamenti della caratteristica

        private void Characteristic_CustomUpdated(object sender, CharacteristicUpdatedEventArgs e)
        {
            // Esegui azioni per gestire gli aggiornamenti della caratteristica qui
            var characteristic = e.Characteristic;
            var value = characteristic.Value[0]; // Ottieni il valore della caratteristica
            Console.WriteLine($"Valore aggiornato della caratteristica: {value}");


            MainThread.BeginInvokeOnMainThread(() =>
            {
                lblCustom.Text = $"Temperatura: {value}";
            });

        }


        private void Characteristic_StringUpdated(object sender, CharacteristicUpdatedEventArgs e)
        {
            // Esegui azioni per gestire gli aggiornamenti della caratteristica qui
            var characteristic = e.Characteristic;
            var value = characteristic.Value; // Ottieni il valore della caratteristica
            string valueString = Encoding.UTF8.GetString(value);
            Console.WriteLine($"Valore aggiornato della customChar: {valueString}");


            MainThread.BeginInvokeOnMainThread(() =>
            {
                lblString.Text = $"Valore: {valueString}";
            });

        }

        //private async void OnSubmitButtonClicked(object sender, EventArgs e)
        //{
        //    try
        //    {
        //        var adapter = CrossBluetoothLE.Current.Adapter;


        //        // Connessione al dispositivo
        //        await adapter.ConnectToDeviceAsync(connectedDevice);

        //        // Ottenere il servizio
        //        var service = await connectedDevice.GetServiceAsync(new Guid("19B10004-E8F2-537E-4F6C-D104768A1214"));
        //        if (service == null)
        //        {
        //            throw new Exception("Servizio non trovato.");
        //        }

        //        // Ottenere la caratteristica
        //        var characteristic = await service.GetCharacteristicAsync(new Guid("19B10005-E8F2-537E-4F6C-D104768A1214"));
        //        if (characteristic == null)
        //        {
        //            throw new Exception("Caratteristica non trovata.");
        //        }

        //        byte value = byte.Parse(valueTb.Text);

        //        // Scrittura del valore sulla caratteristica
        //        await characteristic.WriteAsync(new byte[] { value });

        //        Console.WriteLine("Valore scritto con successo sulla caratteristica.");
        //    }
        //    catch (Exception ex)
        //    {
        //        Console.WriteLine($"Errore durante la scrittura sulla caratteristica: {ex.Message}");
        //    }
        //}

        private async void Picker_SelectedIndexChanged(object sender, EventArgs e)
        {
            try
            {
                //var adapter = CrossBluetoothLE.Current.Adapter;


                // Connessione al dispositivo
                await adapter.ConnectToDeviceAsync(connectedDevice);

                // Ottenere il servizio
                var service = await connectedDevice.GetServiceAsync(new Guid("19B10000-E8F2-537E-4F6C-D104768A1214"));
                if (service == null)
                {
                    throw new Exception("Servizio non trovato.");
                }

                // Ottenere la caratteristica
                var characteristic = await service.GetCharacteristicAsync(new Guid("19B10005-E8F2-537E-4F6C-D104768A1214"));
                if (characteristic == null)
                {
                    throw new Exception("Caratteristica non trovata.");
                }


                byte value = 0;

                if (ledPkr.SelectedIndex == 0)
                    value = 1;

                // Scrittura del valore sulla caratteristica
                await characteristic.WriteAsync(new byte[] { value });

                Console.WriteLine("Valore scritto con successo sulla caratteristica.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Errore durante la scrittura sulla caratteristica: {ex.Message}");
            }
        }

        private void OnPageButtonClicked(object sender, EventArgs e)
        {

            BluetoothDeviceListPage np = new BluetoothDeviceListPage(adapter);
            Navigation.PushAsync(np);
        }
    }


}
